from pawpal_system import Task, Pet, Owner, Scheduler

scheduler = Scheduler()

# --- Setup ---
owner = Owner(name="Alex", preferences={"sort_by": "time"})

dog = Pet(name="Biscuit", species="Dog")
cat = Pet(name="Luna", species="Cat")

# Tasks with explicit priorities (1=high, 2=medium, 3=low)
dog.add_task(Task(description="Evening walk",    start_time="18:00", end_time="18:30", frequency="daily",     priority=2))
dog.add_task(Task(description="Feed breakfast",  start_time="07:30", end_time="07:35", frequency="daily",     priority=1))
dog.add_task(Task(description="Morning walk",    start_time="07:00", end_time="07:30", frequency="daily",     priority=2))
cat.add_task(Task(description="Evening feeding", start_time="17:30", end_time="17:35", frequency="daily",     priority=1))
cat.add_task(Task(description="Clean litter box",start_time="08:00", end_time="08:10", frequency="daily",     priority=3))

# Intentional conflicts to test detect_conflicts
dog.add_task(Task(description="Vet appointment", start_time="07:15", end_time="08:00", frequency="as needed", priority=1))
cat.add_task(Task(description="Grooming",        start_time="17:30", end_time="18:00", frequency="as needed", priority=3))

# Mark one task complete via scheduler (triggers next-occurrence logic)
scheduler.mark_complete(dog.tasks[0], dog)  # Evening walk is done

owner.add_pet(dog)
owner.add_pet(cat)

# --- Schedule sorted by time (default preference) ---
owner.preferences["sort_by"] = "time"
print("=== Schedule sorted by TIME ===")
for pet, task in scheduler.generate_schedule(owner):
    print(f"  [{task.start_time}–{task.end_time}] P{task.priority} {pet.name}: {task.description}")

# --- Schedule sorted by priority ---
owner.preferences["sort_by"] = "priority"
print("\n=== Schedule sorted by PRIORITY (then time as tiebreaker) ===")
for pet, task in scheduler.generate_schedule(owner):
    print(f"  P{task.priority} [{task.start_time}–{task.end_time}] {pet.name}: {task.description}")

# --- Conflict detection ---
print("\n=== Conflict Warnings ===")
conflicts = scheduler.detect_conflicts(owner)
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts detected.")
