from typing import Dict, Literal
from pydantic import BaseModel, Field

class TaskDef(BaseModel):
    id: str
    difficulty: Literal["easy", "medium", "hard"]
    repo_files: Dict[str, str]
    bug: str
    risk: float = Field(ge=0.0, le=1.0)
    developer_comment: str
    expected_decision: str
    description: str
    test_code: str = ""

class Observation(BaseModel):
    task_id: str
    difficulty: Literal["easy", "medium", "hard"]
    repo_files: Dict[str, str]
    bug_hint: str
    risk_score: float
    description: str

class Action(BaseModel):
    bug_type: str
    fix_code: str
    reasoning: str
    decision: Literal["APPROVE", "REQUEST_CHANGES"]

class StepInfo(BaseModel):
    valid: bool
    task_id: str = ""
    task_reward: float = 0.0
    cumulative_score: float = 0.0
    tasks_remaining: int = 0
    error: str = ""
