#!/usr/bin/env python3
"""
Create a better savestate where Link is free to move immediately
"""

from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time

def create_moveable_savestate():
    """Create a savestate where Link can move freely"""
    
    ROM_PATH = "roms/LinksAwakeningDX-Rev2.gbc"
    NEW_STATE_PATH = "roms/LinksAwakeningDX-Rev2-moveable.gbc.state"
    
    # Start emulator
    pyboy = PyBoy(ROM_PATH, window="SDL2", cgb=True)
    pyboy.set_emulation_speed(3)  # Faster to get through intro
    
    print("Starting from the beginning...")
    
    # Wait for the intro to finish (approx 12 seconds at 3x speed)
    for _ in range(60 * 4):  # Reduced time due to 3x speed
        pyboy.tick()
    
    print("Intro complete, navigating menus...")
    
    # Press START to clear the title screen
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    for _ in range(60):
        pyboy.tick()
    
    # Press START again to pick File 1
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    for _ in range(60):
        pyboy.tick()
    
    # Press A to input name (will use default)
    pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
    for _ in range(60):
        pyboy.tick()
    
    # Confirm name
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    for _ in range(60):
        pyboy.tick()
    
    # Select the new file
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    for _ in range(60 * 2):
        pyboy.tick()
    
    print("In-game cutscene begins...")
    print("Waiting for Marin to finish walking in...")
    
    # Wait for Marin's approach
    for _ in range(60 * 1):  # Reduced due to 3x speed
        pyboy.tick()
    
    # Advance through all dialogue quickly
    print("Skipping through Marin's dialogue...")
    for i in range(6):
        print(f"Dialog step {i+1}")
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        for _ in range(15):  # Shorter wait due to faster speed
            pyboy.tick()
    
    print("Dialogue complete, Link should be free to move now!")
    
    # Wait a moment to ensure Link is fully controllable
    for _ in range(60):
        pyboy.tick()
    
    # Test movement to verify Link can move
    print("Testing movement...")
    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    for _ in range(10):
        pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    
    pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
    for _ in range(10):
        pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
    
    print("Movement test complete!")
    
    # Slow down to normal speed for better savestate
    pyboy.set_emulation_speed(1)
    for _ in range(30):
        pyboy.tick()
    
    # Save the new state
    print(f"Saving new savestate to {NEW_STATE_PATH}...")
    with open(NEW_STATE_PATH, "wb") as f:
        pyboy.save_state(f)
    
    pyboy.stop()
    print("✅ New moveable savestate created successfully!")
    print(f"Saved to: {NEW_STATE_PATH}")
    
    return NEW_STATE_PATH

if __name__ == "__main__":
    create_moveable_savestate()