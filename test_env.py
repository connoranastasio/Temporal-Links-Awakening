#!/usr/bin/env python3
"""Quick test of the environment"""

from env.link_env import LinkEnv
import time

print("Creating environment...")
env = LinkEnv(render=False)  # Test headless first

print("Resetting environment...")
obs, info = env.reset()

print(f"Observation shape: {obs.shape}")
print("Environment loaded successfully!")

print("Taking a few random actions...")
for i in range(3):  # Fewer steps for debugging
    print(f"About to take step {i}...")
    action = env.action_space.sample()
    print(f"Action selected: {action}")
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {i} completed: action={action}, reward={reward:.2f}")
    time.sleep(0.5)  # Longer delay to see what happens

print("Closing environment...")
env.close()
print("Test complete!")