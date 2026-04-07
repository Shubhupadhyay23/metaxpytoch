"""
Grader for the AI Code Review Environment.
Evaluates agent actions with partial-credit scoring across 4 dimensions.

Score breakdown (total max = 1.0):
    bug_detection  : 0.30  — correct bug type identified
    fix_quality    : 0.40  — proposed fix executes without error
    reasoning      : 0.20  — reasoning mentions relevant concepts
    decision       : 0.10  — correct approve / request-changes call
"""

from vm.executor import run_code

# Keywords associated with each bug type for partial reasoning credit
BUG_KEYWORDS = {
    "division_by_zero": ["zero", "division", "divide", "denominator", "nan", "infinity"],
    "key_error":        ["key", "missing", "optional", "default", "get(", "dict"],
    "sql_injection":    ["injection", "sanitize", "parameterize", "escape", "query", "input"],
    "race_condition":   ["race", "thread", "lock", "mutex", "atomic", "concurrent", "sync"],
    "memory_leak":      ["leak", "memory", "reference", "garbage", "registry", "cleanup", "weakref"],
}

# Difficulty multiplier — harder tasks grant proportionally more reward
DIFFICULTY_WEIGHT = {
    "easy":   1.0,
    "medium": 1.0,
    "hard":   1.0,
}


def grade(action: dict, task: dict) -> float:
    """
    Grade an agent action against a task definition.

    Returns a float in [0.0, 1.0].
    """
    score = 0.0
    bug = task.get("bug", "")
    difficulty = task.get("difficulty", "easy")

    # ── 1. Bug detection (0.0 – 0.30) ────────────────────────────────────
    detected = action.get("bug_type", "").strip().lower()
    if detected == bug:
        score += 0.30                          # exact match
    elif detected in bug or bug in detected:
        score += 0.15                          # partial match (substring)

    # ── 2. Fix quality (0.0 – 0.40) ──────────────────────────────────────
    fix_code = action.get("fix_code", "")
    if fix_code:
        result = run_code(fix_code)
        if result["status"] == "success":
            score += 0.40
        else:
            # Partial credit: code was provided but has a runtime error
            score += 0.10

    # ── 3. Reasoning quality (0.0 – 0.20) ────────────────────────────────
    reasoning = action.get("reasoning", "").lower()
    keywords = BUG_KEYWORDS.get(bug, [])
    matched = sum(1 for kw in keywords if kw in reasoning)
    if matched >= 2:
        score += 0.20
    elif matched == 1:
        score += 0.10

    # ── 4. Decision correctness (0.0 – 0.10) ─────────────────────────────
    expected = task.get("expected_decision", "REQUEST_CHANGES")
    if action.get("decision") == expected:
        score += 0.10

    # Clamp to [0.0, 1.0] and apply difficulty weight (currently all 1.0)
    score = min(1.0, score) * DIFFICULTY_WEIGHT.get(difficulty, 1.0)
    score = max(0.01, min(0.99, score))
    return round(score, 4)
