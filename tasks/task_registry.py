"""
Task registry for the AI Code Review Environment.
Simulates real-world pull request review scenarios across 5 difficulty levels.
"""

from typing import List
from env.models import TaskDef


def load_tasks() -> List[TaskDef]:
    """Load all 5 tasks ordered from easy to hard, using Pydantic validation."""
    return [
        # ── TASK 1 ── EASY ─────────────────────────────────────────────────
        TaskDef(
            id="task1",
            difficulty="easy",
            repo_files={
                "main.py": (
                    "from fastapi import FastAPI, HTTPException\n"
                    "import os\n\n"
                    "app = FastAPI()\n\n"
                    "@app.get('/download/{filename}')\n"
                    "def download_file(filename: str):\n"
                    "    file_path = os.path.join('/var/www/uploads', filename)\n"
                    "    if not os.path.exists(file_path):\n"
                    "        raise HTTPException(status_code=404, detail='File not found')\n"
                    "    with open(file_path, 'r') as f:\n"
                    "        return f.read()\n"
                ),
            },
            bug="path_traversal",
            risk=0.9,
            developer_comment="Added endpoint to download user uploads.",
            expected_decision="REQUEST_CHANGES",
            description=(
                "A FastAPI endpoint allows downloading files from an uploads directory. "
                "Identify the path traversal vulnerability and suggest a secure fix."
            ),
            test_code=(
                "import os\n"
                "from fastapi import HTTPException\n"
                "try:\n"
                "    download_file('../../../etc/passwd')\n"
                "    raise Exception('Path traversal succeeded!')\n"
                "except HTTPException as e:\n"
                "    assert e.status_code in [403, 404]\n"
            )
        ),
        # ── TASK 2 ── EASY ─────────────────────────────────────────────────
        TaskDef(
            id="task2",
            difficulty="easy",
            repo_files={
                "config.py": (
                    "import yaml\n\n"
                    "def load_config(yaml_string: str) -> dict:\n"
                    "    # Load user configuration securely\n"
                    "    return yaml.load(yaml_string)\n"
                ),
            },
            bug="unsafe_yaml",
            risk=0.85,
            developer_comment="Using PyYAML to load custom user configurations.",
            expected_decision="REQUEST_CHANGES",
            description=(
                "A configuration module uses yaml.load to parse untrusted strings. "
                "Identify the remote code execution vulnerability and propose a safe loading mechanism."
            ),
            test_code=(
                "import yaml\n"
                "try:\n"
                "    load_config('!!python/object/apply:os.system [\"echo pwned\"]')\n"
                "    raise Exception('RCE payload executed!')\n"
                "except yaml.constructor.ConstructorError:\n"
                "    pass\n"
            )
        ),
        # ── TASK 3 ── MEDIUM ───────────────────────────────────────────────
        TaskDef(
            id="task3",
            difficulty="medium",
            repo_files={
                "db_service.py": (
                    "import sqlite3\n\n"
                    "def get_user_by_name(conn, username: str):\n"
                    "    query = f\"SELECT * FROM users WHERE name = '{username}'\"\n"
                    "    cursor = conn.execute(query)\n"
                    "    return cursor.fetchall()\n"
                ),
            },
            bug="sql_injection",
            risk=0.95,
            developer_comment="This is internal tooling, only used by admins.",
            expected_decision="REQUEST_CHANGES",
            description=(
                "A database query is built using string interpolation with user input. "
                "Identify the SQL injection vector and provide a parameterized fix."
            ),
            test_code=(
                "import sqlite3\n"
                "conn = sqlite3.connect(':memory:')\n"
                "conn.execute('CREATE TABLE users (name TEXT, role TEXT)')\n"
                "conn.execute(\"INSERT INTO users VALUES ('admin', 'admin')\")\n"
                "get_user_by_name(conn, \"admin' OR '1'=='1\")\n"
            )
        ),
        # ── TASK 4 ── MEDIUM ───────────────────────────────────────────────
        TaskDef(
            id="task4",
            difficulty="medium",
            repo_files={
                "inventory.py": (
                    "import asyncio\n\n"
                    "inventory = {'item_1': 100}\n\n"
                    "async def purchase_item(user_id: str):\n"
                    "    stock = inventory['item_1']\n"
                    "    if stock > 0:\n"
                    "        await asyncio.sleep(0.1)  # simulate payment processing\n"
                    "        inventory['item_1'] = stock - 1\n"
                    "        return True\n"
                    "    return False\n"
                ),
            },
            bug="race_condition",
            risk=0.8,
            developer_comment="Asyncio doesn't need locks because of the GIL, right?",
            expected_decision="REQUEST_CHANGES",
            description=(
                "An async purchase function reads inventory, waits for payment, and writes back. "
                "Identify the async race condition and fix it using asyncio primitives."
            ),
            test_code=(
                "import asyncio\n"
                "async def test():\n"
                "    await asyncio.gather(*[purchase_item(str(i)) for i in range(110)])\n"
                "    # Should not result in negative stock if handled properly"
            )
        ),
        # ── TASK 5 ── HARD ─────────────────────────────────────────────────
        TaskDef(
            id="task5",
            difficulty="hard",
            repo_files={
                "manager.py": (
                    "class ConnectionManager:\n"
                    "    connections = []\n\n"
                    "    def __init__(self, client_id):\n"
                    "        self.client_id = client_id\n"
                    "        ConnectionManager.connections.append(self)\n\n"
                    "    def disconnect(self):\n"
                    "        print(f'Client {self.client_id} disconnected')\n"
                    "        # self is never removed from ConnectionManager.connections\n"
                ),
            },
            bug="memory_leak",
            risk=0.7,
            developer_comment="Connections are managed via a central class registry.",
            expected_decision="REQUEST_CHANGES",
            description=(
                "A connection manager appends instances to a class-level list but never "
                "removes them upon disconnect. Identify the memory leak and implement proper cleanup."
            ),
            test_code=(
                "import weakref\n"
                "mgr = ConnectionManager('client1')\n"
                "ref = weakref.ref(mgr)\n"
                "mgr.disconnect()\n"
                "del mgr\n"
                "# In a correct implementation, ref() should be None, meaning it got collected"
            )
        ),
    ]
