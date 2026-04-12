"""
CodingReviewEnv — OpenEnv-compliant environment for AI code review.

Implements the full OpenEnv interface:
    reset()  → Observation
    step()   → (Observation | {}, reward, done, info)
    state()  → dict with session metadata
"""

from __future__ import annotations
from typing import Any, Dict, Literal, List, Tuple
from pydantic import ValidationError

from tasks.task_registry import load_tasks
from graders.grader import grade
from env.models import TaskDef, Observation, Action, StepInfo


def _task_to_observation(task: TaskDef) -> dict:
    """Convert internal task dict → public Observation schema."""
    obs = Observation(
        task_id=task.id,
        difficulty=task.difficulty,
        repo_files=task.repo_files,
        bug_hint=task.bug,
        risk_score=task.risk,
        description=task.description,
    )
    return obs.model_dump()


class CodingReviewEnv:
    """
    Observation space and Action space are validated via Pydantic.
    Reward: float in [0.0, 1.0] with partial credits per dimension.
    """

    def __init__(self):
        self.tasks: List[TaskDef] = load_tasks()
        self.index: int = 0
        self.scores: List[float] = []
        self.errors: List[str] = []

    # ── OpenEnv interface ────────────────────────────────────────────────

    def reset(self) -> dict:
        """Reset to the first task and return its observation."""
        self.index = 0
        self.scores = []
        self.errors = []
        if not self.tasks:
            return {}
        return _task_to_observation(self.tasks[0])

    def step(self, action_dict: dict) -> Tuple[dict, float, bool, dict]:
        """
        Apply action to the current task.

        Returns:
            observation : next task observation (or {} if done)
            reward      : float in [0.0, 1.0]
            done        : True when all tasks completed
            info        : dict with per-dimension scores and validation errors
        """
        # Validate action
        try:
            action = Action(**action_dict)
        except ValidationError as e:
            err = str(e)
            self.errors.append(err)
            info = StepInfo(valid=False, error=err).model_dump()
            return _task_to_observation(self.tasks[self.index]), 0.001, False, info

        task = self.tasks[self.index]
        reward = grade(action, task)
        self.scores.append(reward)

        self.index += 1
        done = self.index >= len(self.tasks)
        next_obs = {} if done else _task_to_observation(self.tasks[self.index])

        info = StepInfo(
            valid=True,
            task_id=task.id,
            task_reward=reward,
            cumulative_score=round(sum(self.scores), 4),
            tasks_remaining=len(self.tasks) - self.index,
        ).model_dump()
        
        return next_obs, reward, done, info

    def state(self) -> dict:
        """Return current session state."""
        return {
            "current_task_index": self.index,
            "total_tasks": len(self.tasks),
            "tasks_completed": len(self.scores),
            "scores": self.scores,
            "cumulative_score": round(sum(self.scores), 4),
            "mean_score": round(sum(self.scores) / len(self.scores), 4) if self.scores else 0.0,
            "errors": self.errors,
            "done": self.index >= len(self.tasks),
        }
