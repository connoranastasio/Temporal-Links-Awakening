#!/usr/bin/env python3
"""Test state loading specifically"""

from pyboy import PyBoy

print("Creating PyBoy...")
pyboy = PyBoy("roms/LinksAwakeningDX-Rev2.gbc", window="null", cgb=True, sound=False, sound_emulated=False)
pyboy.set_emulation_speed(1)

print("Testing a few ticks before state load...")
for i in range(5):
    pyboy.tick()
    print(f"Tick {i+1} successful")

print("Now attempting to load base.state...")
with open("roms/base.state", "rb") as f:
    pyboy.load_state(f)
print("State loaded successfully!")

print("Testing ticks after state load...")
for i in range(3):
    pyboy.tick()
    print(f"Post-load tick {i+1} successful")

pyboy.stop()
print("State loading test completed!")