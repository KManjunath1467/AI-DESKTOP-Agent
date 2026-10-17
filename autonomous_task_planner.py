from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set, Dict
import heapq
import re


class Intent(Enum):
    SEARCH = "SEARCH"
    ANALYZE = "ANALYZE"
    MODIFY = "MODIFY"
    COMMUNICATE = "COMMUNICATE"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


@dataclass
class Task:
    task_id: str
    description: str
    intent: Intent
    priority: int
    dependencies: Set[str] = field(default_factory=set)
    estimated_cost: int = 1


@dataclass
class ExecutionPlan:
    goal: str
    tasks: List[Task]
    confidence: float


class IntentDetector:

    KEYWORDS = {
        Intent.SEARCH: {
            "find", "search", "locate", "look", "discover"
        },
        Intent.ANALYZE: {
            "analyze", "analyse", "compare", "summarize", "inspect"
        },
        Intent.MODIFY: {
            "edit", "modify", "change", "update", "rename"
        },
        Intent.COMMUNICATE: {
            "send", "message", "email", "notify"
        },
        Intent.SYSTEM: {
            "system", "cpu", "memory", "process", "performance"
        }
    }

    def detect(self, text: str) -> Intent:

        words = set(
            re.findall(r"[a-z]+", text.lower())
        )

        scores = {
            intent: len(words & keywords)
            for intent, keywords in self.KEYWORDS.items()
        }

        best = max(
            scores,
            key=scores.get
        )

        return (
            best
            if scores[best] > 0
            else Intent.UNKNOWN
        )


class TaskPlanner:

    def __init__(self):
        self.detector = IntentDetector()

    def create_plan(self, request: str) -> ExecutionPlan:

        intent = self.detector.detect(request)

        tasks = []

        if intent == Intent.ANALYZE:

            tasks = [
                Task(
                    "discover",
                    "Discover relevant information",
                    Intent.SEARCH,
                    5
                ),
                Task(
                    "collect",
                    "Collect required information",
                    Intent.SEARCH,
                    6,
                    {"discover"}
                ),
                Task(
                    "analyze",
                    "Analyze collected information",
                    Intent.ANALYZE,
                    8,
                    {"collect"}
                ),
                Task(
                    "summarize",
                    "Create structured summary",
                    Intent.ANALYZE,
                    7,
                    {"analyze"}
                ),
                Task(
                    "validate",
                    "Validate final result",
                    Intent.ANALYZE,
                    9,
                    {"summarize"}
                )
            ]

        elif intent == Intent.MODIFY:

            tasks = [
                Task(
                    "locate",
                    "Locate requested target",
                    Intent.SEARCH,
                    7
                ),
                Task(
                    "inspect",
                    "Inspect target state",
                    Intent.ANALYZE,
                    8,
                    {"locate"}
                ),
                Task(
                    "plan_change",
                    "Construct safe modification plan",
                    Intent.MODIFY,
                    9,
                    {"inspect"}
                ),
                Task(
                    "apply",
                    "Apply modification",
                    Intent.MODIFY,
                    10,
                    {"plan_change"}
                ),
                Task(
                    "verify",
                    "Verify modification",
                    Intent.ANALYZE,
                    9,
                    {"apply"}
                )
            ]

        else:

            tasks = [
                Task(
                    "interpret",
                    "Interpret user request",
                    intent,
                    8
                ),
                Task(
                    "execute",
                    "Execute planned operation",
                    intent,
                    9,
                    {"interpret"}
                ),
                Task(
                    "verify",
                    "Verify operation",
                    Intent.ANALYZE,
                    7,
                    {"execute"}
                )
            ]

        return ExecutionPlan(
            goal=request,
            tasks=tasks,
            confidence=0.91 if intent != Intent.UNKNOWN else 0.25
        )

    def schedule(
        self,
        plan: ExecutionPlan
    ) -> List[Task]:

        remaining = {
            task.task_id: task
            for task in plan.tasks
        }

        completed = set()
        schedule = []

        while remaining:

            available = [
                task
                for task in remaining.values()
                if task.dependencies <= completed
            ]

            if not available:
                raise RuntimeError(
                    "Circular dependency detected"
                )

            available.sort(
                key=lambda x: (
                    -x.priority,
                    x.estimated_cost
                )
            )

            task = available[0]

            schedule.append(task)
            completed.add(task.task_id)
            del remaining[task.task_id]

        return schedule


if __name__ == "__main__":

    planner = TaskPlanner()

    request = (
        "Analyze the research and summarize "
        "the important findings"
    )

    plan = planner.create_plan(request)

    print("GOAL:")
    print(plan.goal)

    print("\nCONFIDENCE:", plan.confidence)

    print("\nEXECUTION PLAN:")

    for index, task in enumerate(
        planner.schedule(plan),
        start=1
    ):
        print(
            f"{index}. "
            f"[P{task.priority}] "
            f"{task.description}"
        )
