#!/usr/bin/env python3
"""Minimal PyBoy test without state loading"""

from pyboy import PyBoy
import time

print("Testing basic PyBoy initialization...")
pyboy = PyBoy("roms/LinksAwakeningDX-Rev2.gbc", window="null", cgb=True, sound=False, sound_emulated=False)
print("PyBoy created successfully!")

print("Setting speed to 1...")
pyboy.set_emulation_speed(1)

print("Testing single tick...")
pyboy.tick()
print("First tick successful!")

print("Testing second tick...")
pyboy.tick()
print("Second tick successful!")

print("Testing memory access...")
health = pyboy.memory[0xDB5A]
print(f"Health value: {health}")

pyboy.stop()
print("Test completed successfully!")