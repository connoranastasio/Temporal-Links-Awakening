#!/usr/bin/env python3
"""Test video recording functionality"""

import os
import gymnasium as gym
from stable_baselines3.common.vec_env import DummyVecEnv, VecVideoRecorder
from stable_baselines3.common.monitor import Monitor
from env.link_env import LinkEnv

def make_env():
    env = LinkEnv(render=True)  # Need render=True for video recording
    env = Monitor(env)
    return env

def main():
    os.makedirs("test_videos", exist_ok=True)
    
    print("Creating environment for video recording...")
    env = DummyVecEnv([make_env])
    
    # Record every episode for testing (normally we'd use a trigger)
    env = VecVideoRecorder(
        env, 
        video_folder="test_videos", 
        record_video_trigger=lambda x: True,  # Record every episode
        video_length=200,  # Short video (200 frames)
        name_prefix="test_episode"
    )
    
    print("Starting video recording test...")
    obs = env.reset()
    
    # Take 200 random actions to create a short video
    for i in range(200):
        action = [env.action_space.sample()]
        obs, reward, done, info = env.step(action)
        
        if i % 50 == 0:
            print(f"Frame {i}/200, reward: {reward[0]:.2f}")
        
        if done[0]:
            print("Episode ended, resetting...")
            obs = env.reset()
    
    print("Closing environment...")
    env.close()
    
    print("Video test complete! Check test_videos/ folder for output.")

if __name__ == "__main__":
    main()