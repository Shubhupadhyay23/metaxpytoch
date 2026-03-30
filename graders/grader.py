from vm.executor import run_code

def grade(action, task):
    score = 0

    # 1. bug detection
    if action.get("bug_type") == task["bug"]:
        score += 0.3

    # 2. fix execution
    if "fix_code" in action:
        result = run_code(action["fix_code"])
        if result["status"] == "success":
            score += 0.4

    # 3. reasoning quality
    reasoning = action.get("reasoning", "").lower()
    if "error" in reasoning or "exception" in reasoning:
        score += 0.2

    # 4. decision
    if action.get("decision") == "REQUEST_CHANGES":
        score += 0.1

    return score
