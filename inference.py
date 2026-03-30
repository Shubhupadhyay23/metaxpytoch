from env.coding_review_env import CodingReviewEnv

def agent(obs):
    return {
        "bug_type": "division_by_zero",
        "fix_code": "def divide(a,b): return a/b if b!=0 else 0",
        "reasoning": "division by zero error possible",
        "decision": "REQUEST_CHANGES"
    }

env = CodingReviewEnv()
obs = env.reset()

done = False
while not done:
    action = agent(obs)
    obs, reward, done, _ = env.step(action)
    print("Reward:", reward)
