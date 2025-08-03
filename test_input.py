#!/usr/bin/env python3
"""Test programmatic input to PyBoy"""

from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time

print("Creating PyBoy...")
pyboy = PyBoy("roms/LinksAwakeningDX-Rev2.gbc", window="SDL2", cgb=True)
pyboy.set_emulation_speed(1)

print("Game started. Testing programmatic inputs...")
print("Press Ctrl+C to stop")

try:
    frame_count = 0
    while True:
        # Programmatically press A button every 60 frames (1 second)
        if frame_count % 60 == 0:
            print("Sending A button press...")
            pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        
        # Programmatically press arrow keys every 120 frames  
        elif frame_count % 120 == 30:
            print("Sending Down arrow...")
            pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
            
        pyboy.tick()
        frame_count += 1
        time.sleep(0.016)  # ~60 FPS
        
except KeyboardInterrupt:
    print("\nStopping...")

pyboy.stop()
print("Test complete!")