import pytest
from env.coding_review_env import CodingReviewEnv

def test_env_initialization():
    env = CodingReviewEnv()
    assert len(env.tasks) == 5
    assert env.index == 0
    assert len(env.scores) == 0

def test_env_reset():
    env = CodingReviewEnv()
    env.index = 2
    env.scores = [1.0, 0.5]
    obs = env.reset()
    assert env.index == 0
    assert len(env.scores) == 0
    assert 'task_id' in obs
    assert obs['task_id'] == 'task1'
    assert 'description' in obs

def test_env_step_invalid_action():
    env = CodingReviewEnv()
    env.reset()
    # Invalid action missing fields
    invalid_action = {"bug_type": "some_bug"}
    obs, reward, done, info = env.step(invalid_action)
    assert not info["valid"]
    assert "error" in info
    # The score should be minimal and index should not advance
    assert reward == 0.001
    assert env.index == 0

def test_env_step_valid_action():
    env = CodingReviewEnv()
    env.reset()
    valid_action = {
        "bug_type": "path_traversal",
        "fix_code": "def download_file(): pass",
        "reasoning": "Missing sanitize path",
        "decision": "REQUEST_CHANGES"
    }
    obs, reward, done, info = env.step(valid_action)
    assert info["valid"]
    assert env.index == 1
    assert reward > 0.0
    assert reward < 1.0

def test_env_state():
    env = CodingReviewEnv()
    env.reset()
    state = env.state()
    assert state["total_tasks"] == 5
    assert not state["done"]
