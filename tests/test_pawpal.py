from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(description="Feed", start="08:00", end="08:30", frequency="daily", priority=2):
    return Task(description=description, start_time=start, end_time=end, frequency=frequency, priority=priority)


def make_owner_with_pet(*tasks, sort_by="time"):
    pet = Pet(name="Biscuit", species="Dog")
    for t in tasks:
        pet.add_task(t)
    owner = Owner(name="Alice", preferences={"sort_by": sort_by})
    owner.add_pet(pet)
    return owner, pet


# ---------------------------------------------------------------------------
# Task defaults
# ---------------------------------------------------------------------------

def test_task_default_priority():
    task = Task(description="Walk", start_time="07:00", end_time="07:30", frequency="daily")
    assert task.priority == 2


def test_task_default_is_complete():
    task = Task(description="Walk", start_time="07:00", end_time="07:30", frequency="daily")
    assert task.is_complete is False


def test_task_default_due_date_is_today():
    task = Task(description="Walk", start_time="07:00", end_time="07:30", frequency="daily")
    assert task.due_date == date.today().isoformat()


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    pet = Pet(name="Biscuit", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


def test_remove_task_by_description():
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(make_task("Walk"))
    pet.add_task(make_task("Feed"))
    pet.remove_task("Walk")
    assert all(t.description != "Walk" for t in pet.tasks)
    assert len(pet.tasks) == 1


def test_remove_task_removes_all_matching():
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(make_task("Walk"))
    pet.add_task(make_task("Walk"))
    pet.remove_task("Walk")
    assert pet.tasks == []


def test_remove_task_nonexistent_no_crash():
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(make_task("Feed"))
    pet.remove_task("Nonexistent")
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

def test_get_all_tasks_flattens_multiple_pets():
    pet1 = Pet(name="Biscuit", species="Dog", tasks=[make_task("Walk")])
    pet2 = Pet(name="Whiskers", species="Cat", tasks=[make_task("Feed"), make_task("Play")])
    owner = Owner(name="Alice")
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    assert len(owner.get_all_tasks()) == 3


def test_get_all_tasks_no_pets():
    owner = Owner(name="Alice")
    assert owner.get_all_tasks() == []


# ---------------------------------------------------------------------------
# Scheduler.get_pending_tasks
# ---------------------------------------------------------------------------

def test_get_pending_tasks_excludes_complete():
    t1 = make_task("Walk")
    t2 = make_task("Feed")
    t2.is_complete = True
    owner, _ = make_owner_with_pet(t1, t2)
    scheduler = Scheduler()
    pending = scheduler.get_pending_tasks(owner)
    assert len(pending) == 1
    assert pending[0][1].description == "Walk"


def test_get_pending_tasks_empty_owner():
    owner = Owner(name="Alice")
    assert Scheduler().get_pending_tasks(owner) == []


def test_get_pending_tasks_all_complete():
    t = make_task()
    t.is_complete = True
    owner, _ = make_owner_with_pet(t)
    assert Scheduler().get_pending_tasks(owner) == []


# ---------------------------------------------------------------------------
# Scheduler.organize_by_time
# ---------------------------------------------------------------------------

def test_organize_by_time_sorts_ascending():
    pet = Pet(name="Biscuit", species="Dog")
    pairs = [
        (pet, make_task("C", start="10:00", end="10:30")),
        (pet, make_task("A", start="07:00", end="07:30")),
        (pet, make_task("B", start="09:00", end="09:30")),
    ]
    result = Scheduler().organize_by_time(pairs)
    descriptions = [t.description for _, t in result]
    assert descriptions == ["A", "B", "C"]


def test_organize_by_time_same_start_no_crash():
    pet = Pet(name="Biscuit", species="Dog")
    pairs = [
        (pet, make_task("X", start="08:00", end="08:30")),
        (pet, make_task("Y", start="08:00", end="08:45")),
    ]
    result = Scheduler().organize_by_time(pairs)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Scheduler.organize_by_priority
# ---------------------------------------------------------------------------

def test_organize_by_priority_high_before_low():
    pet = Pet(name="Biscuit", species="Dog")
    pairs = [
        (pet, make_task("Low", priority=3, start="07:00", end="07:30")),
        (pet, make_task("High", priority=1, start="09:00", end="09:30")),
    ]
    result = Scheduler().organize_by_priority(pairs)
    assert result[0][1].description == "High"


def test_organize_by_priority_tiebreak_by_time():
    pet = Pet(name="Biscuit", species="Dog")
    pairs = [
        (pet, make_task("Later", priority=2, start="10:00", end="10:30")),
        (pet, make_task("Earlier", priority=2, start="08:00", end="08:30")),
    ]
    result = Scheduler().organize_by_priority(pairs)
    assert result[0][1].description == "Earlier"


# ---------------------------------------------------------------------------
# Scheduler.mark_complete
# ---------------------------------------------------------------------------

def test_mark_complete_sets_is_complete():
    _, pet = make_owner_with_pet()
    task = make_task(frequency="as needed")
    pet.add_task(task)
    Scheduler().mark_complete(task, pet)
    assert task.is_complete is True


def test_mark_complete_daily_adds_next_task():
    _, pet = make_owner_with_pet()
    task = make_task("Feed", frequency="daily")
    today = date.today().isoformat()
    task.due_date = today
    pet.add_task(task)
    Scheduler().mark_complete(task, pet)
    new_tasks = [t for t in pet.tasks if not t.is_complete]
    assert len(new_tasks) == 1
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert new_tasks[0].due_date == expected


def test_mark_complete_weekly_adds_next_task():
    _, pet = make_owner_with_pet()
    task = make_task("Bath", frequency="weekly")
    pet.add_task(task)
    Scheduler().mark_complete(task, pet)
    new_tasks = [t for t in pet.tasks if not t.is_complete]
    assert len(new_tasks) == 1
    expected = (date.today() + timedelta(weeks=1)).isoformat()
    assert new_tasks[0].due_date == expected


def test_mark_complete_recurring_preserves_fields():
    _, pet = make_owner_with_pet()
    task = make_task("Walk", start="07:00", end="07:30", frequency="daily", priority=1)
    pet.add_task(task)
    Scheduler().mark_complete(task, pet)
    new_task = next(t for t in pet.tasks if not t.is_complete)
    assert new_task.description == "Walk"
    assert new_task.start_time == "07:00"
    assert new_task.end_time == "07:30"
    assert new_task.priority == 1
    assert new_task.frequency == "daily"


def test_mark_complete_as_needed_no_new_task():
    _, pet = make_owner_with_pet()
    task = make_task(frequency="as needed")
    pet.add_task(task)
    before = len(pet.tasks)
    Scheduler().mark_complete(task, pet)
    assert len(pet.tasks) == before


# ---------------------------------------------------------------------------
# Scheduler.detect_conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_overlapping_tasks():
    t1 = make_task("Walk", start="08:00", end="09:00")
    t2 = make_task("Feed", start="08:30", end="09:30")
    owner, _ = make_owner_with_pet(t1, t2)
    warnings = Scheduler().detect_conflicts(owner)
    assert len(warnings) == 1


def test_detect_conflicts_adjacent_tasks_no_conflict():
    t1 = make_task("Walk", start="08:00", end="09:00")
    t2 = make_task("Feed", start="09:00", end="09:30")
    owner, _ = make_owner_with_pet(t1, t2)
    warnings = Scheduler().detect_conflicts(owner)
    assert warnings == []


def test_detect_conflicts_no_overlap():
    t1 = make_task("Walk", start="07:00", end="07:30")
    t2 = make_task("Feed", start="09:00", end="09:30")
    owner, _ = make_owner_with_pet(t1, t2)
    assert Scheduler().detect_conflicts(owner) == []


def test_detect_conflicts_across_pets():
    pet1 = Pet(name="Biscuit", species="Dog", tasks=[make_task("Walk", start="08:00", end="09:00")])
    pet2 = Pet(name="Whiskers", species="Cat", tasks=[make_task("Feed", start="08:30", end="09:30")])
    owner = Owner(name="Alice")
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    warnings = Scheduler().detect_conflicts(owner)
    assert len(warnings) == 1


def test_detect_conflicts_completed_tasks_ignored():
    t1 = make_task("Walk", start="08:00", end="09:00")
    t2 = make_task("Feed", start="08:30", end="09:30")
    t2.is_complete = True
    owner, _ = make_owner_with_pet(t1, t2)
    assert Scheduler().detect_conflicts(owner) == []


def test_detect_conflicts_single_task():
    owner, _ = make_owner_with_pet(make_task())
    assert Scheduler().detect_conflicts(owner) == []


def test_detect_conflicts_no_tasks():
    owner = Owner(name="Alice")
    assert Scheduler().detect_conflicts(owner) == []


# ---------------------------------------------------------------------------
# Scheduler.generate_schedule
# ---------------------------------------------------------------------------

def test_generate_schedule_sort_by_time():
    t1 = make_task("Later", start="10:00", end="10:30", priority=1)
    t2 = make_task("Earlier", start="07:00", end="07:30", priority=3)
    owner, _ = make_owner_with_pet(t1, t2, sort_by="time")
    result = Scheduler().generate_schedule(owner)
    assert result[0][1].description == "Earlier"


def test_generate_schedule_sort_by_priority():
    t1 = make_task("LowPriLate", start="07:00", end="07:30", priority=3)
    t2 = make_task("HighPriEarly", start="10:00", end="10:30", priority=1)
    owner, _ = make_owner_with_pet(t1, t2, sort_by="priority")
    result = Scheduler().generate_schedule(owner)
    assert result[0][1].description == "HighPriEarly"


def test_generate_schedule_excludes_complete():
    t1 = make_task("Done", start="07:00", end="07:30")
    t1.is_complete = True
    t2 = make_task("Pending", start="09:00", end="09:30")
    owner, _ = make_owner_with_pet(t1, t2)
    result = Scheduler().generate_schedule(owner)
    assert len(result) == 1
    assert result[0][1].description == "Pending"
