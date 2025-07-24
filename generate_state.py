import time
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from pathlib import Path

ROM_PATH = "roms/LinksAwakeningDX-Rev2.gbc"
STATE_PATH = "roms/LinksAwakeningDX-Rev2.gbc.state"

# Start emulator with CGB mode enabled
pyboy = PyBoy(ROM_PATH, window="null", cgb=True)
pyboy.set_emulation_speed(0)

# Wait for the intro to finish (approx 12 seconds)
for _ in range(60 * 12):
    pyboy.tick()

print("Intro video complete")

# Press START to clear the title screen
pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
pyboy.tick()
pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
for _ in range(60):  # Wait 1 second
    pyboy.tick()
print("Title menu loaded")

# Press START again to pick File 1
pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
pyboy.tick()
pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
for _ in range(60):
    pyboy.tick()
print("File select menu loaded")

# Press A to input name (will use default "a")
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

print("In-game cutscene begins")
print("Waiting for Marin to finish walking in")

# Wait for Marin's approach (roughly 3 seconds)
for _ in range(60 * 3):
    pyboy.tick()

# Advance through all six lines of Marin's dialogue
for i in range(6):
    print(f"Marin dialog step {i+1}")
    pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
    for _ in range(45):  # Wait for dialog to finish appearing
        pyboy.tick()

# Save the state to file
print("Saving state...")
with open(STATE_PATH, "wb") as f:
    pyboy.save_state(f)

pyboy.stop()
print("State saved successfully.")
