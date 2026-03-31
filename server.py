from flask import Flask, request, jsonify
from env.coding_review_env import CodingReviewEnv

app = Flask(__name__)
env = CodingReviewEnv()

@app.route("/", methods=["GET", "POST"])
def index():
    return jsonify({"status": "API is running! Visit /state, /reset, or POST to /step"})

@app.route("/reset", methods=["GET", "POST"])
def reset():
    return jsonify(env.reset())

@app.route("/step", methods=["POST"])
def step():
    action = request.json
    obs, reward, done, _ = env.step(action)
    return jsonify({
        "observation": obs,
        "reward": reward,
        "done": done
    })

@app.route("/state", methods=["GET", "POST"])
def state():
    return jsonify(env.state())

def main():
    app.run(host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
