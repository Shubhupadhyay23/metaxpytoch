"""
Task registry for the AI Code Review Environment.
Simulates real-world pull request review scenarios across 5 difficulty levels.
"""

from typing import List, Dict, Any


def load_tasks() -> List[Dict[str, Any]]:
    """Load all 5 tasks ordered from easy to hard."""
    return [
        # ── TASK 1 ── EASY ─────────────────────────────────────────────────
        {
            "id": "task1",
            "difficulty": "easy",
            "repo_files": {
                "math_utils.py": (
                    "def divide(a, b):\n"
                    "    return a / b\n\n"
                    "result = divide(10, 0)  # called by downstream service\n"
                ),
            },
            "bug": "division_by_zero",
            "risk": 0.9,
            "developer_comment": "This utility has been stable for months, no issues.",
            "expected_decision": "REQUEST_CHANGES",
            "description": (
                "A utility function is called with a zero denominator in production. "
                "Identify the bug and propose a safe fix."
            ),
        },
        # ── TASK 2 ── EASY ─────────────────────────────────────────────────
        {
            "id": "task2",
            "difficulty": "easy",
            "repo_files": {
                "user_service.py": (
                    "def get_display_name(user: dict) -> str:\n"
                    "    return user['first_name'] + ' ' + user['last_name']\n\n"
                    "def get_email(user: dict) -> str:\n"
                    "    return user['email']\n"
                ),
            },
            "bug": "key_error",
            "risk": 0.75,
            "developer_comment": "Users always have first_name and email set.",
            "expected_decision": "REQUEST_CHANGES",
            "description": (
                "A user profile service crashes when optional fields are absent. "
                "Identify unsafe dictionary access and suggest defensive code."
            ),
        },
        # ── TASK 3 ── MEDIUM ───────────────────────────────────────────────
        {
            "id": "task3",
            "difficulty": "medium",
            "repo_files": {
                "db_service.py": (
                    "import sqlite3\n\n"
                    "def get_user_by_name(conn, username: str):\n"
                    "    query = f\"SELECT * FROM users WHERE name = '{username}'\"\n"
                    "    cursor = conn.execute(query)\n"
                    "    return cursor.fetchall()\n"
                ),
            },
            "bug": "sql_injection",
            "risk": 0.95,
            "developer_comment": "This is internal tooling, only used by admins.",
            "expected_decision": "REQUEST_CHANGES",
            "description": (
                "A database query is built using string interpolation with user input. "
                "Identify the SQL injection vector and provide a parameterized fix."
            ),
        },
        # ── TASK 4 ── MEDIUM ───────────────────────────────────────────────
        {
            "id": "task4",
            "difficulty": "medium",
            "repo_files": {
                "counter_service.py": (
                    "import threading\n\n"
                    "counter = 0\n\n"
                    "def increment():\n"
                    "    global counter\n"
                    "    temp = counter\n"
                    "    # simulate processing delay\n"
                    "    counter = temp + 1\n\n"
                    "threads = [threading.Thread(target=increment) for _ in range(100)]\n"
                    "for t in threads: t.start()\n"
                    "for t in threads: t.join()\n"
                ),
            },
            "bug": "race_condition",
            "risk": 0.8,
            "developer_comment": "Threading is fine here, reads and writes are atomic.",
            "expected_decision": "REQUEST_CHANGES",
            "description": (
                "A shared counter is mutated by multiple threads without synchronization. "
                "Identify the race condition and suggest a thread-safe solution."
            ),
        },
        # ── TASK 5 ── HARD ─────────────────────────────────────────────────
        {
            "id": "task5",
            "difficulty": "hard",
            "repo_files": {
                "cache_service.py": (
                    "class Cache:\n"
                    "    _registry = []\n\n"
                    "    def __init__(self, name: str):\n"
                    "        self.name = name\n"
                    "        self.data = {}\n"
                    "        Cache._registry.append(self)  # never cleaned up\n\n"
                    "    def store(self, key: str, value: object):\n"
                    "        self.data[key] = value\n\n"
                    "    def clear(self):\n"
                    "        self.data = {}\n"
                    "        # BUG: instance still held in _registry\n"
                ),
            },
            "bug": "memory_leak",
            "risk": 0.7,
            "developer_comment": "Cache is cleared when no longer needed.",
            "expected_decision": "REQUEST_CHANGES",
            "description": (
                "A cache class appends itself to a class-level registry on construction "
                "but never removes itself. Identify the memory leak and fix the lifecycle."
            ),
        },
    ]
