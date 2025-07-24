from stable_baselines3 import PPO
from env.link_env import LinkEnv
from utils.log_manager import FrameLogger

env = LinkEnv(render=True)
model = PPO.load("models/ppo_link")

logger = FrameLogger(diff_threshold=0.05)

obs = env.reset()
while True:
    action, _ = model.predict(obs)
    obs, reward, done, _ = env.step(action)

    logger.log_if_different(obs)

    if done:
        break
