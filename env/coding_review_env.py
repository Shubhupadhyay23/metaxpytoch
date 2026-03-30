from tasks.task_registry import load_tasks
from graders.grader import grade

class CodingReviewEnv:
    def __init__(self):
        self.tasks = load_tasks()
        self.index = 0

    def reset(self):
        self.index = 0
        return self.tasks[self.index]

    def step(self, action):
        task = self.tasks[self.index]

        reward = grade(action, task)

        self.index += 1
        done = self.index >= len(self.tasks)

        next_state = self.tasks[self.index] if not done else {}

        return next_state, reward, done, {}

    def state(self):
        return {"current_task": self.index}
