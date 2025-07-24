from pyboy import PyBoy
from pyboy.utils import WindowEvent
import os

ROM_PATH = "roms/LinksAwakening-Rev2.gb"
STATE_PATH = "states/overworld_start.state"
os.makedirs("states", exist_ok=True)

pyboy = PyBoy(ROM_PATH, window_type="headless")
pyboy.set_emulation_speed(0)  # Max speed

def tick(frames, log=None):
    for _ in range(frames):
        pyboy.tick()
    if log:
        print(log)

def press(button, hold=3, rest=2):
    pyboy.send_input(button)
    tick(hold)
    pyboy.send_input(button + 0x10)  # RELEASE
    tick(rest)

# --- Boot + intro ---
tick(1500, "Intro video complete")

# --- Menu navigation ---
press(WindowEvent.PRESS_BUTTON_START, 5, 5)  # pass title screen
tick(60, "Title menu loaded")

press(WindowEvent.PRESS_BUTTON_START, 5, 5)  # select File 1
tick(60, "File select menu loaded")

press(WindowEvent.PRESS_BUTTON_A, 5, 5)      # accept default name
tick(30)

press(WindowEvent.PRESS_BUTTON_START, 5, 5)  # confirm name
tick(60)

press(WindowEvent.PRESS_BUTTON_START, 5, 5)  # begin game
tick(180, "In-game cutscene begins")

# --- Marin's intro dialogue ---
tick(240, "Waiting for Marin to finish walking in")

for i in range(6):
    press(WindowEvent.PRESS_BUTTON_A, 3, 5)
    tick(40, f"Marin dialog step {i+1}")

# --- Save state when player gains control ---
print("Saving state...")
pyboy.save_state(STATE_PATH)
pyboy.stop()
print(f"Saved to {STATE_PATH}")
