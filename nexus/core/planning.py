"""Planning engine and task tree utilities."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from nexus.agents.base import Task


class TaskTree(BaseModel):
    goal: str
    tasks: list[Task] = Field(default_factory=list)
    completed: dict[str, dict[str, Any]] = Field(default_factory=dict)
    failed: dict[str, str] = Field(default_factory=dict)

    def get_ready_tasks(self) -> list[Task]:
        done = set(self.completed.keys())
        failed = set(self.failed.keys())
        ready: list[Task] = []
        for task in self.tasks:
            if task.id in done or task.id in failed:
                continue
            if all(dep in done for dep in task.dependencies):
                ready.append(task)
        return ready

    def mark_complete(self, task_id: str, result: dict[str, Any]) -> None:
        self.completed[task_id] = result

    def mark_failed(self, task_id: str, error: str) -> None:
        self.failed[task_id] = error

    def is_complete(self) -> bool:
        return len(self.completed) == len(self.tasks)

    def get_failed_tasks(self) -> list[str]:
        return list(self.failed.keys())

    def merge(self, new_plan: "TaskTree") -> None:
        existing = {t.id for t in self.tasks}
        for task in new_plan.tasks:
            if task.id not in existing:
                self.tasks.append(task)


@dataclass(slots=True)
class ExecutionGraph:
    layers: list[list[str]]


class PlanningEngine:
    """Hierarchical task planner with static fallback decomposition."""

    def decompose(self, goal: str, context: dict[str, Any]) -> TaskTree:
        del context
        base = [
            Task(id=str(uuid4()), title="Research", description=f"Research for goal: {goal}", agent_type="research", parallel=True, priority=1, tools_needed=["web_search"], success_criteria="Sufficient references"),
            Task(id=str(uuid4()), title="Build", description=f"Build output artifacts for: {goal}", agent_type="code", dependencies=[], parallel=True, priority=2, tools_needed=["code_executor"], success_criteria="Runnable artifacts"),
            Task(id=str(uuid4()), title="Validate", description=f"Validate deliverables for: {goal}", agent_type="qa", dependencies=[], parallel=False, priority=3, tools_needed=[], success_criteria="QA score >= 0.6"),
        ]
        base[2].dependencies = [base[0].id, base[1].id]
        return TaskTree(goal=goal, tasks=base)

    def replan(self, failed_task: Task, error: str, attempts: int) -> TaskTree:
        if attempts == 1:
            tasks = [failed_task]
        elif attempts == 2:
            tasks = [Task(**(failed_task.model_dump() | {"id": str(uuid4()), "description": f"Simplified: {failed_task.description}"}))]
        elif attempts == 3:
            t1 = Task(id=str(uuid4()), title=f"Split A {failed_task.title}", description=failed_task.description[: len(failed_task.description) // 2], agent_type=failed_task.agent_type)
            t2 = Task(id=str(uuid4()), title=f"Split B {failed_task.title}", description=failed_task.description[len(failed_task.description) // 2 :], agent_type=failed_task.agent_type, dependencies=[t1.id])
            tasks = [t1, t2]
        elif attempts == 4:
            alt = "code" if failed_task.agent_type != "code" else "research"
            tasks = [Task(**(failed_task.model_dump() | {"id": str(uuid4()), "agent_type": alt, "description": f"Alternative tool route after: {error}"}))]
        else:
            tasks = [Task(id=str(uuid4()), title="Escalate to human", description=f"Escalation required: {error}", agent_type="file")]
        return TaskTree(goal=f"Replan:{failed_task.title}", tasks=tasks)

    def prioritize(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: (t.priority, t.estimated_steps, len(t.dependencies)))

    def identify_parallelism(self, task_tree: TaskTree) -> ExecutionGraph:
        indegree: dict[str, int] = defaultdict(int)
        children: dict[str, list[str]] = defaultdict(list)
        for t in task_tree.tasks:
            indegree[t.id] += 0
            for dep in t.dependencies:
                children[dep].append(t.id)
                indegree[t.id] += 1
        queue = deque([task_id for task_id, deg in indegree.items() if deg == 0])
        layers: list[list[str]] = []
        while queue:
            layer_size = len(queue)
            layer: list[str] = []
            for _ in range(layer_size):
                node = queue.popleft()
                layer.append(node)
                for ch in children[node]:
                    indegree[ch] -= 1
                    if indegree[ch] == 0:
                        queue.append(ch)
            layers.append(layer)
        return ExecutionGraph(layers=layers)
