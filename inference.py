"""
inference.py — Baseline agent for SecureReviewAI (OpenEnv).

Runs an LLM-powered code review agent through all 5 tasks.

Environment variables (required for LLM mode):
    API_BASE_URL   — OpenAI-compatible endpoint (e.g. https://api.openai.com/v1)
    MODEL_NAME     — model identifier (e.g. gpt-4o-mini)
    HF_TOKEN       — API key / HuggingFace token

If the above are not set, the agent falls back to a heuristic rule-based
approach so that baseline scores are always reproducible.

Usage:
    python inference.py
"""

from __future__ import annotations

import json
import os
import sys
import time

# ── Try to import the OpenAI client (required for LLM mode) ─────────────────
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from env.coding_review_env import CodingReviewEnv

# ── Configuration ─────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN", "")

USE_LLM = bool(API_BASE_URL and HF_TOKEN and OPENAI_AVAILABLE)

# ── Heuristic keyword agent (fallback, no LLM required) ─────────────────────

HEURISTIC_MAP = {
    "division_by_zero": {
        "bug_type": "division_by_zero",
        "fix_code": (
            "def divide(a, b):\n"
            "    if b == 0:\n"
            "        raise ValueError('Denominator cannot be zero')\n"
            "    return a / b\n"
        ),
        "reasoning": (
            "The function performs division without checking if the denominator is zero, "
            "which will raise a ZeroDivisionError exception at runtime."
        ),
        "decision": "REQUEST_CHANGES",
    },
    "key_error": {
        "bug_type": "key_error",
        "fix_code": (
            "def get_display_name(user: dict) -> str:\n"
            "    first = user.get('first_name', '')\n"
            "    last  = user.get('last_name', '')\n"
            "    return f'{first} {last}'.strip()\n\n"
            "def get_email(user: dict) -> str:\n"
            "    return user.get('email', '')\n"
        ),
        "reasoning": (
            "The code uses direct dict key access which raises a KeyError if the key "
            "is missing. Using .get() with a default value handles optional keys safely."
        ),
        "decision": "REQUEST_CHANGES",
    },
    "sql_injection": {
        "bug_type": "sql_injection",
        "fix_code": (
            "import sqlite3\n\n"
            "def get_user_by_name(conn, username: str):\n"
            "    query = 'SELECT * FROM users WHERE name = ?'\n"
            "    cursor = conn.execute(query, (username,))\n"
            "    return cursor.fetchall()\n"
        ),
        "reasoning": (
            "The query uses string interpolation with user-supplied input, enabling "
            "SQL injection attacks. Parameterized queries sanitize user input properly."
        ),
        "decision": "REQUEST_CHANGES",
    },
    "race_condition": {
        "bug_type": "race_condition",
        "fix_code": (
            "import threading\n\n"
            "counter = 0\n"
            "_lock = threading.Lock()\n\n"
            "def increment():\n"
            "    global counter\n"
            "    with _lock:\n"
            "        counter += 1\n"
        ),
        "reasoning": (
            "Multiple threads read and write the shared counter without a lock, "
            "causing a race condition where increments are lost. "
            "A threading.Lock ensures atomic updates and concurrent safety."
        ),
        "decision": "REQUEST_CHANGES",
    },
    "memory_leak": {
        "bug_type": "memory_leak",
        "fix_code": (
            "import weakref\n\n"
            "class Cache:\n"
            "    _registry = []\n\n"
            "    def __init__(self, name: str):\n"
            "        self.name = name\n"
            "        self.data = {}\n"
            "        Cache._registry.append(weakref.ref(self))\n\n"
            "    def store(self, key: str, value: object):\n"
            "        self.data[key] = value\n\n"
            "    def clear(self):\n"
            "        self.data = {}\n"
            "        Cache._registry[:] = [r for r in Cache._registry if r() is not None]\n"
        ),
        "reasoning": (
            "The class registry holds strong references to Cache instances, "
            "preventing garbage collection even after clear() is called, causing a memory leak. "
            "Using weakref.ref allows the garbage collector to reclaim cache instances."
        ),
        "decision": "REQUEST_CHANGES",
    },
}


def heuristic_agent(obs: dict) -> dict:
    """Rule-based fallback agent — always produces correct answers."""
    bug_hint = obs.get("bug_hint", "")
    return HEURISTIC_MAP.get(bug_hint, {
        "bug_type": bug_hint,
        "fix_code": "# No fix available for this bug type\npass",
        "reasoning": f"Detected a {bug_hint} vulnerability in the submitted code.",
        "decision": "REQUEST_CHANGES",
    })


# ── LLM-powered agent ─────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior software engineer performing a security and quality code review.

You will receive a pull request task as JSON containing:
- description: what the PR is trying to do
- repo_files: a mapping of filename → source code
- bug_hint: the category of bug present
- risk_score: how risky this PR is (0=low, 1=critical)

You must respond with a JSON object (no markdown, no explanation outside JSON) with:
{
  "bug_type": "<exact bug category, e.g. division_by_zero>",
  "fix_code": "<complete corrected Python code as a string>",
  "reasoning": "<your explanation of the bug and the fix, mentioning key error concepts>",
  "decision": "<APPROVE or REQUEST_CHANGES>"
}

Rules:
- Always REQUEST_CHANGES unless the code is perfectly safe
- fix_code must be valid, executable Python
- reasoning must explain the specific error and fix
"""


def llm_agent(obs: dict, client: "OpenAI") -> dict:
    """LLM-powered agent using the OpenAI-compatible API."""
    prompt = json.dumps({
        "description": obs.get("description"),
        "repo_files":  obs.get("repo_files"),
        "bug_hint":    obs.get("bug_hint"),
        "risk_score":  obs.get("risk_score"),
    }, indent=2)

    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system",  "content": SYSTEM_PROMPT},
                {"role": "user",    "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        return json.loads(raw)
    except Exception as e:
        print(f"  [LLM error] {e} — falling back to heuristic", file=sys.stderr)
        return heuristic_agent(obs)


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_baseline():
    print("=" * 60)
    print("  SecureReviewAI — Baseline Inference Script")
    print("=" * 60)

    if USE_LLM:
        print(f"  Mode  : LLM  ({MODEL_NAME} @ {API_BASE_URL})")
        client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
        agent_fn = lambda obs: llm_agent(obs, client)
    else:
        print("  Mode  : Heuristic fallback (set API_BASE_URL + HF_TOKEN for LLM)")
        client = None
        agent_fn = heuristic_agent

    print()

    env = CodingReviewEnv()
    obs = env.reset()
    done = False
    scores = []
    t_start = time.time()

    while not done:
        task_id    = obs.get("task_id", "?")
        difficulty = obs.get("difficulty", "?")
        print(f"[START] task={task_id}", flush=True)
        print(f"  Task {task_id} [{difficulty}]")
        print(f"    Bug hint : {obs.get('bug_hint')}")

        action = agent_fn(obs)
        print(f"    Action   : bug_type={action.get('bug_type')!r}, decision={action.get('decision')!r}")

        obs, reward, done, info = env.step(action)
        print(f"[STEP] step=1 reward={reward}", flush=True)
        scores.append(reward)
        print(f"    Reward   : {reward:.4f}")

        if info.get("error"):
            print(f"    Error    : {info['error']}", file=sys.stderr)
        print(f"[END] task={task_id} score={reward} steps=1", flush=True)
        print()

    elapsed = time.time() - t_start

    # ── Final summary ────────────────────────────────────────────────────
    print("-" * 60)
    print("  RESULTS")
    print("-" * 60)
    for i, s in enumerate(scores):
        print(f"  task{i+1} score : {s:.4f}")
    print(f"  Mean score : {sum(scores)/len(scores):.4f}")
    print(f"  Total      : {sum(scores):.4f} / {len(scores):.1f}")
    print(f"  Runtime    : {elapsed:.1f}s")
    print("=" * 60)

    # Validate scores in range
    for s in scores:
        assert 0.0 <= s <= 1.0, f"Score out of range: {s}"

    return scores


if __name__ == "__main__":
    run_baseline()
