from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Tuple


@dataclass
class Task:
    description: str
    start_time: str
    end_time: str
    frequency: str
    priority: int = 2  # 1 = high, 2 = medium, 3 = low
    is_complete: bool = False
    due_date: str = field(default_factory=lambda: date.today().isoformat())


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> None:
        """Remove all tasks matching the given description."""
        self.tasks = [t for t in self.tasks if t.description != description]


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=lambda: {"sort_by": "time"})

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def get_pending_tasks(self, owner: Owner) -> List[Tuple[Pet, Task]]:
        """Return all incomplete (pet, task) pairs across the owner's pets."""
        return [(pet, task) for pet in owner.pets for task in pet.tasks if not task.is_complete]

    def organize_by_time(self, tasks: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
        """Sort (pet, task) pairs in ascending order by start time."""
        return sorted(tasks, key=lambda pair: tuple(int(x) for x in pair[1].start_time.split(":")))

    def organize_by_priority(self, tasks: List[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
        """Sort (pet, task) pairs by priority (1=high first), then by start time as tiebreaker."""
        return sorted(tasks, key=lambda pair: (pair[1].priority, pair[1].start_time))

    def mark_complete(self, task: Task, pet: Pet) -> None:
        """Mark a task as complete and schedule the next occurrence for daily/weekly tasks."""
        task.is_complete = True
        if task.frequency == "daily":
            delta = timedelta(days=1)
        elif task.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return
        next_date = date.fromisoformat(task.due_date) + delta
        pet.add_task(Task(
            description=task.description,
            start_time=task.start_time,
            end_time=task.end_time,
            frequency=task.frequency,
            priority=task.priority,
            due_date=next_date.isoformat(),
        ))

    def detect_conflicts(self, owner: Owner) -> List[str]:
        """Return warning messages for any two pending tasks whose time windows overlap."""
        pending = self.get_pending_tasks(owner)
        warnings = []
        for i in range(len(pending)):
            for j in range(i + 1, len(pending)):
                pet_a, task_a = pending[i]
                pet_b, task_b = pending[j]
                # Intervals overlap when one starts before the other ends
                if task_a.start_time < task_b.end_time and task_b.start_time < task_a.end_time:
                    warnings.append(
                        f"CONFLICT: {pet_a.name}/\"{task_a.description}\" "
                        f"[{task_a.start_time}–{task_a.end_time}] overlaps with "
                        f"{pet_b.name}/\"{task_b.description}\" "
                        f"[{task_b.start_time}–{task_b.end_time}]"
                    )
        return warnings

    def generate_schedule(self, owner: Owner) -> List[Tuple[Pet, Task]]:
        """Return pending (pet, task) pairs sorted according to owner preferences."""
        pending = self.get_pending_tasks(owner)
        if owner.preferences.get("sort_by") == "priority":
            return self.organize_by_priority(pending)
        return self.organize_by_time(pending)
