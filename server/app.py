"""
server/app.py — OpenEnv-compliant Flask application for SecureReviewAI.

This file is the canonical entry point required by OpenEnv multi-mode deployment.
The root server.py imports and re-exports from here for backward compatibility.
"""

import sys
import os

# Ensure the project root is on the path (needed when running from server/ subdir)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from env.coding_review_env import CodingReviewEnv
from tasks.task_registry import load_tasks

app = Flask(__name__)
env = CodingReviewEnv()


@app.route("/", methods=["GET", "POST"])
def index():
    return jsonify({
        "status": "ok",
        "name": "secure-review-ai",
        "version": "0.1.0",
        "description": "AI Code Review Environment — OpenEnv compliant",
        "endpoints": ["/reset", "/step", "/state", "/tasks"],
    })


@app.route("/reset", methods=["GET", "POST"])
def reset():
    obs = env.reset()
    return jsonify(obs)


@app.route("/step", methods=["POST"])
def step():
    action = request.get_json(force=True, silent=True)
    if action is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    obs, reward, done, info = env.step(action)
    return jsonify({
        "observation": obs,
        "reward":      reward,
        "done":        done,
        "info":        info,
    })


@app.route("/state", methods=["GET", "POST"])
def state():
    return jsonify(env.state())


@app.route("/tasks", methods=["GET"])
def tasks():
    """Enumerate all tasks with metadata (used by validator)."""
    task_list = load_tasks()
    return jsonify({
        "total": len(task_list),
        "tasks": [
            {
                "id":          t["id"],
                "difficulty":  t["difficulty"],
                "bug":         t["bug"],
                "risk":        t["risk"],
                "description": t["description"],
            }
            for t in task_list
        ],
    })


def main():
    app.run(host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
