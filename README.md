---
title: SecureReviewAI — AI Code Review Environment
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# SecureReviewAI — OpenEnv Code Review Environment

<div align="center">
  <h3><a href="https://youtu.be/your-video-link">🎥 Watch the Demo Video Here</a></h3>
  <p><i>An autonomous PyTorch-backed code review agent playing the OpenEnv challenge.</i></p>
</div>

<br>

### 🔥 Problem Statement
Modern codebases frequently suffer from silent, hard-to-catch vulnerabilities (e.g., race conditions, memory leaks, SQL injections). Human code review is slow and error-prone, meaning critical bugs often slip into production undetected.

### 💡 Solution Idea
**SecureReviewAI** is an OpenEnv reinforcement learning environment that simulates real-world **pull request code review** workflows. We train and benchmark autonomous AI agents to act as reliable **senior engineers**—identifying threats, testing fixes, and catching bugs *before* they are merged.

### 🧠 How PyTorch is utilized
Our underlying agent logic relies on **Meta-Llama-3**, which utilizes PyTorch for lightning-fast backend inference via our chosen infrastructure providers. The tensor manipulations and scalable memory management native to PyTorch architectures allow our Reflexion validation loops to safely and asynchronously iterate over code structures.

### ⚙️ Setup Steps (Copy-Paste)
Run the agent in just a few seconds.

#### Run with Docker
```bash
docker build -t secure-review-ai .
docker run -p 7860:7860 \
  -e API_BASE_URL=https://api.together.xyz/v1 \
  -e MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct \
  -e HF_TOKEN=your_api_key_here \
  secure-review-ai
```

#### Run Locally
```bash
# Export credentials
export API_BASE_URL=https://api.together.xyz/v1
export MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
export HF_TOKEN=your_api_key_here

# Install and execute
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python inference.py
```

### 📊 Results & Outputs
When the agent operates on the 5 open tasks using our advanced verification prompts, it outputs structurally perfect scores validating both functional syntax and reasoning comprehension.

```bash
[START] task=task5 env=SecureReviewAI model=meta-llama/Meta-Llama-3-8B-Instruct
  Task task5 [hard]
    Bug hint : memory_leak
    Action   : bug_type='memory_leak', decision='REQUEST_CHANGES'
[STEP] step=1 action={"bug_type":"memory_leak","fix_code":"...","reasoning":"...","decision":"REQUEST_CHANGES"} reward=0.99 done=true error=null
    Reward   : 0.9900
[END] task=task5 success=true steps=1 score=0.99 rewards=0.99

------------------------------------------------------------
  RESULTS
------------------------------------------------------------
  task1 score : 0.9900
  task2 score : 0.9900
  task3 score : 0.9900
  task4 score : 0.9900
  task5 score : 0.9900
  Mean score : 0.9900
  Total      : 4.9500 / 5.0
============================================================
```

## 🏗️ Environment Description

**SecureReviewAI** presents agents with 5 increasingly complex real-world code review tasks:

| Task | Difficulty | Bug Type | Risk |
|------|-----------|-----------|------|
| task1 | Easy | Division by Zero | 0.9 |
| task2 | Easy | Key Error (unsafe dict access) | 0.75 |
| task3 | Medium | SQL Injection | 0.95 |
| task4 | Medium | Race Condition | 0.80 |
| task5 | Hard | Memory Leak | 0.70 |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET\|POST | `/` | Health check |
| GET\|POST | `/reset` | Reset env, returns first observation |
| POST | `/step` | Submit action, receive reward |
| GET\|POST | `/state` | Current session state |
| GET | `/tasks` | List all tasks |

## 🔭 Observation Space

```json
{
  "task_id":    "task1",
  "difficulty": "easy",
  "repo_files": { "math_utils.py": "def divide(a, b): return a / b" },
  "bug_hint":   "division_by_zero",
  "risk_score": 0.9,
  "description": "A utility function is called with a zero denominator..."
}
```

## 🎮 Action Space

```json
{
  "bug_type":  "division_by_zero",
  "fix_code":  "def divide(a, b):\n    if b == 0: raise ValueError(...)\n    return a / b",
  "reasoning": "The function divides without checking if b is zero, causing a ZeroDivisionError.",
  "decision":  "REQUEST_CHANGES"
}
```

## 🏆 Reward Function

Each action is scored across 4 dimensions (total max = **1.0**):

| Dimension | Max Score | Criteria |
|-----------|-----------|----------|
| Bug Detection | 0.30 | Exact bug type match |
| Fix Quality | 0.40 | Fix code executes without error |
| Reasoning | 0.20 | Reasoning mentions 2+ relevant keywords |
| Decision | 0.10 | Correct APPROVE / REQUEST_CHANGES |

## 🚀 Setup Instructions

### Run with Docker

```bash
docker build -t secure-review-ai .
docker run -p 7860:7860 \
  -e API_BASE_URL=https://api.together.xyz/v1 \
  -e MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct \
  -e HF_TOKEN=your_api_key_here \
  secure-review-ai
```



| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE_URL` | For LLM mode | OpenAI-compatible API endpoint |
| `MODEL_NAME` | For LLM mode | Model identifier (default: `meta-llama/Meta-Llama-3-8B-Instruct`) |
| `HF_TOKEN` | For LLM mode | API key / HuggingFace token |

## 📋 Example REST Session
If you're querying the server manually alongside the inference agent:

```bash
# 1. Reset
curl -X POST http://localhost:7860/reset

# 2. Submit a review action
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "bug_type": "division_by_zero",
    "fix_code": "def divide(a, b):\n    if b == 0: raise ValueError(\"Cannot divide by zero\")\n    return a / b",
    "reasoning": "The function divides without checking if the denominator is zero, causing a division error.",
    "decision": "REQUEST_CHANGES"
  }'

# 3. Check state
curl http://localhost:7860/state
```

## 🗂️ Project Structure

```
.
├── server.py              # Flask API server
├── inference.py           # Baseline agent (LLM + heuristic modes)
├── openenv.yaml           # OpenEnv spec
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
├── uv.lock                # Locked dependency versions
├── env/
│   └── coding_review_env.py   # Environment logic
├── tasks/
│   └── task_registry.py       # 5 task definitions
├── graders/
│   └── grader.py              # Partial-credit reward function
└── vm/
    └── executor.py            # Safe code execution sandbox
```
