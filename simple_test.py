#!/usr/bin/env python3
"""Simple test without reward calculation"""

from env.link_env import LinkEnv
import time

print("Creating environment...")
env = LinkEnv(render=False)

print("Manually setting speed to 1...")
env.pyboy.set_emulation_speed(1)

print("Resetting environment...")
obs, info = env.reset()

print("Setting speed to 1 again after reset...")
env.pyboy.set_emulation_speed(1)

print("Testing basic PyBoy operations...")
print("Getting memory value...")
health = env.pyboy.memory[0xDB5A]
print(f"Health: {health}")

print("Getting screen image...")
screen = env.pyboy.screen.image
print(f"Screen size: {screen.size}")

print("Testing single tick...")
try:
    env.pyboy.tick()
    print("Single tick successful!")
except Exception as e:
    print(f"Tick failed: {e}")

env.close()
print("Test complete!")