---
title: SecureReviewAI — AI Code Review Environment
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# SecureReviewAI — OpenEnv Code Review Environment

An AI environment that simulates real-world **pull request code review** workflows.
Agents act as senior engineers reviewing code for bugs, security vulnerabilities, and quality issues.

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
  -e API_BASE_URL=https://api.openai.com/v1 \
  -e MODEL_NAME=gpt-4o-mini \
  -e HF_TOKEN=your_token_here \
  secure-review-ai
```

### Run locally

```bash
pip install -r requirements.txt
python server.py
```

### Run inference baseline

```bash
# With LLM (requires env vars)
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=your_api_key

# Without LLM (heuristic fallback — always works)
python inference.py
```

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE_URL` | For LLM mode | OpenAI-compatible API endpoint |
| `MODEL_NAME` | For LLM mode | Model identifier (default: `gpt-4o-mini`) |
| `HF_TOKEN` | For LLM mode | API key / HuggingFace token |

## 📋 Example Session

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
