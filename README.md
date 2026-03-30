# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Running the tests

```bash
source .venv/bin/activate
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains 31 tests across six areas:

| Area | What is verified |
| --- | --- |
| **Task defaults** | `priority`, `is_complete`, and `due_date` are set correctly on construction |
| **Pet management** | `add_task` grows the list; `remove_task` removes all matching descriptions including duplicates; removing a non-existent description does not crash |
| **Owner aggregation** | `get_all_tasks` flattens tasks across multiple pets; works correctly with no pets |
| **Sorting correctness** | `organize_by_time` returns tasks in chronological order; `organize_by_priority` puts high-priority tasks first and breaks ties by start time; `generate_schedule` dispatches to the correct sort based on owner preferences |
| **Recurrence logic** | Completing a `daily` task adds a new task due the next day; completing a `weekly` task adds one due 7 days later; `as needed` tasks produce no new task; the new task preserves all original fields (description, times, priority, frequency) |
| **Conflict detection** | Overlapping time windows produce a warning; adjacent tasks (end == start) do not; completed tasks are excluded from conflict checks; conflicts are detected across different pets |

### Confidence level

★★★★☆ (4/5)

The core scheduling behaviors — sorting, recurrence, and conflict detection — are all verified and passing. Confidence is high for the logic layer. One star is held back because the Streamlit UI (`app.py`) has no automated tests, so end-to-end user interactions are untested.
