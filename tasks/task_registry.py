def load_tasks():
    return [
        {
            "id": "task1",
            "repo_files": {
                "main.py": "def divide(a,b): return a/b"
            },
            "bug": "division_by_zero",
            "risk": 0.9,
            "developer_comment": "This works fine"
        },
        {
            "id": "task2",
            "repo_files": {
                "app.py": "def get_name(user): return user['name']"
            },
            "bug": "key_error",
            "risk": 0.8,
            "developer_comment": "Tested already"
        }
    ]
