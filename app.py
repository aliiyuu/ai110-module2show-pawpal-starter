import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
else:
    st.session_state.owner.name = owner_name

sort_by = st.selectbox("Schedule sort order", ["time", "priority"], help="Sort tasks by start time, or by priority (high first) with time as tiebreaker")
st.session_state.owner.preferences["sort_by"] = sort_by

# --- Pets ---
st.markdown("### Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(pet)

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table([
        {"Name": p.name, "Species": p.species, "Tasks": len(p.tasks)}
        for p in st.session_state.owner.pets
    ])
else:
    st.info("No pets yet. Add one above.")

# --- Tasks ---
st.markdown("### Tasks")
st.caption("Select a pet and add tasks to them.")

if st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Add task to", pet_names)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        start_time = st.text_input("Start time (HH:MM)", value="07:00")
    with col3:
        end_time = st.text_input("End time (HH:MM)", value="07:30")
    with col4:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
    with col5:
        priority = st.selectbox("Priority", [1, 2, 3], index=1, format_func=lambda p: {1: "1 - High", 2: "2 - Medium", 3: "3 - Low"}[p])

    if st.button("Add task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        selected_pet.add_task(Task(description=task_title, start_time=start_time, end_time=end_time, frequency=frequency, priority=priority))

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table([
            {"Pet": p.name, "Task": t.description, "Priority": t.priority, "Start": t.start_time, "End": t.end_time, "Frequency": t.frequency, "Due": t.due_date}
            for p in st.session_state.owner.pets
            for t in p.tasks
        ])
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

# --- Schedule ---
st.subheader("Build Schedule")
st.caption("Generates a schedule from all pending tasks across all pets, sorted by start time.")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

if st.button("Generate schedule"):
    st.session_state.schedule = st.session_state.scheduler.generate_schedule(st.session_state.owner)

if "schedule" in st.session_state:
    conflicts = st.session_state.scheduler.detect_conflicts(st.session_state.owner)
    if conflicts:
        for warning in conflicts:
            st.warning(warning)

    st.subheader("Today's Schedule")
    if st.session_state.schedule:
        header = st.columns([1, 3, 1, 2, 2, 2, 2])
        for col, label in zip(header, ["Done", "Task", "P", "Pet", "Time", "Frequency", "Due"]):
            col.markdown(f"**{label}**")
        st.divider()
        for i, (pet, task) in enumerate(st.session_state.schedule):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 3, 1, 2, 2, 2, 2])
            with col1:
                checked = st.checkbox("", value=task.is_complete, key=f"task_{pet.name}_{task.description}_{task.due_date}")
                if checked and not task.is_complete:
                    st.session_state.scheduler.mark_complete(task, pet)
                    st.session_state.schedule = st.session_state.scheduler.generate_schedule(st.session_state.owner)
                    st.rerun()
            col2.write(task.description)
            col3.write(task.priority)
            col4.write(pet.name)
            col5.write(f"{task.start_time}–{task.end_time}")
            col6.write(task.frequency)
            col7.write(task.due_date)
    else:
        st.info("No pending tasks to schedule.")
