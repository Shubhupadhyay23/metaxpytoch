"""
CodingReviewEnv — OpenEnv-compliant environment for AI code review.

Implements the full OpenEnv interface:
    reset()  → Observation
    step()   → (Observation | {}, reward, done, info)
    state()  → dict with session metadata
"""

from __future__ import annotations
from typing import Any, Dict, Literal, List, Tuple

from tasks.task_registry import load_tasks
from graders.grader import grade


# ── Typed model helpers (no external deps, pure dicts with validation) ──────

VALID_DECISIONS = {"APPROVE", "REQUEST_CHANGES"}
REQUIRED_ACTION_FIELDS = {"bug_type", "fix_code", "reasoning", "decision"}


def _validate_action(action: dict) -> Tuple[bool, str]:
    """Return (is_valid, error_message)."""
    if not isinstance(action, dict):
        return False, "Action must be a JSON object"
    missing = REQUIRED_ACTION_FIELDS - action.keys()
    if missing:
        return False, f"Missing fields: {sorted(missing)}"
    if action.get("decision") not in VALID_DECISIONS:
        return False, f"decision must be one of {VALID_DECISIONS}"
    return True, ""


def _task_to_observation(task: dict) -> dict:
    """Convert internal task dict → public Observation schema."""
    return {
        "task_id":    task["id"],
        "difficulty": task["difficulty"],
        "repo_files": task["repo_files"],
        "bug_hint":   task["bug"],          # exposed so agents have context
        "risk_score": task["risk"],
        "description": task["description"],
    }


class CodingReviewEnv:
    """
    Observation space:
        task_id    : str          — unique task identifier
        difficulty : str          — easy | medium | hard
        repo_files : dict[str,str]— filename → source code
        bug_hint   : str          — the category of bug present
        risk_score : float        — 0.0–1.0 risk level
        description: str          — natural language task description

    Action space:
        bug_type   : str          — identified bug category
        fix_code   : str          — corrected Python code
        reasoning  : str          — agent's explanation
        decision   : str          — APPROVE | REQUEST_CHANGES

    Reward: float in [0.0, 1.0] with partial credits per dimension.
    """

    def __init__(self):
        self.tasks: List[dict] = load_tasks()
        self.index: int = 0
        self.scores: List[float] = []
        self.errors: List[str] = []

    # ── OpenEnv interface ────────────────────────────────────────────────

    def reset(self) -> dict:
        """Reset to the first task and return its observation."""
        self.index = 0
        self.scores = []
        self.errors = []
        return _task_to_observation(self.tasks[0])

    def step(self, action: dict) -> Tuple[dict, float, bool, dict]:
        """
        Apply action to the current task.

        Returns:
            observation : next task observation (or {} if done)
            reward      : float in [0.0, 1.0]
            done        : True when all tasks completed
            info        : dict with per-dimension scores and validation errors
        """
        # Validate action
        valid, err = _validate_action(action)
        if not valid:
            self.errors.append(err)
            info = {"error": err, "valid": False}
            return _task_to_observation(self.tasks[self.index]), 0.01, False, info

        task = self.tasks[self.index]
        reward = grade(action, task)
        self.scores.append(reward)

        self.index += 1
        done = self.index >= len(self.tasks)
        next_obs = {} if done else _task_to_observation(self.tasks[self.index])

        info = {
            "valid": True,
            "task_id": task["id"],
            "task_reward": reward,
            "cumulative_score": round(sum(self.scores), 4),
            "tasks_remaining": len(self.tasks) - self.index,
        }
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
