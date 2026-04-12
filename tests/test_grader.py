import pytest
from graders.grader import grade
from env.models import Action, TaskDef

def test_grader_score_bounds():
    task = TaskDef(
        id="test_task",
        difficulty="easy",
        repo_files={},
        bug="sql_injection",
        risk=0.9,
        developer_comment="",
        expected_decision="REQUEST_CHANGES",
        description="",
        test_code="assert True"
    )
    
    # Perfect action
    action = Action(
        bug_type="sql_injection",
        fix_code="x = 1",
        reasoning="sanitize parameterize input query",
        decision="REQUEST_CHANGES"
    )
    
    score = grade(action, task)
    assert score > 0.0
    assert score < 1.0 # Due to the strict exclusive clamp
    assert score == 0.999 # Max score clamped

def test_grader_partial_score():
    task = TaskDef(
        id="test_task",
        difficulty="easy",
        repo_files={},
        bug="memory_leak",
        risk=0.9,
        developer_comment="",
        expected_decision="REQUEST_CHANGES",
        description="",
        test_code="raise Exception('Fail')"
    )
    
    # Action gets some things wrong, tests fail
    action = Action(
        bug_type="memory_leak",
        fix_code="x = 1",
        reasoning="I dunno",
        decision="APPROVE"
    )
    
    score = grade(action, task)
    # bug match: 0.3
    # fix quality: 0.1 (failed test)
    # reasoning: 0.0 (no keywords)
    # decision: 0.0 (wrong decision)
    # Total ~ 0.4
    assert abs(score - 0.4) < 0.01

def test_grader_invalid_fix_code_but_good_reasoning():
    task = TaskDef(
        id="test_task",
        difficulty="medium",
        repo_files={},
        bug="unsafe_yaml",
        risk=0.8,
        developer_comment="",
        expected_decision="REQUEST_CHANGES",
        description="",
        test_code="raise Exception('Fail')"
    )
    
    # Action gets some things wrong, tests fail
    action = Action(
        bug_type="unsafe_yaml",
        fix_code="print(1/0)",
        reasoning="yaml safe_load is requested",
        decision="REQUEST_CHANGES"
    )
    
    score = grade(action, task)
    # bug match: 0.3
    # fix quality: 0.1 (execution error)
    # reasoning: 0.2 (2+ keywords)
    # decision: 0.1 (correct)
    # Total ~ 0.7
    assert abs(score - 0.70) < 0.01
