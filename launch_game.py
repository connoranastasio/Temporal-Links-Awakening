from pyboy import PyBoy
import threading
import time
import os
from datetime import datetime
import sys

# Check for monitoring flag
enable_monitoring = "--monitor" in sys.argv
item_monitor = None

if enable_monitoring:
    try:
        from item_flag_monitor import ItemFlagMonitor
        print("🔍 Item monitoring enabled!")
    except ImportError:
        print("❌ Could not import item_flag_monitor, running without monitoring")
        enable_monitoring = False

# Launch the game and keep it open
pyboy = PyBoy("roms/LinksAwakeningDX-Rev2.gbc", window="SDL2", cgb=True)
pyboy.set_emulation_speed(1)  # Normal speed for manual control

# Initialize monitoring if enabled
if enable_monitoring:
    item_monitor = ItemFlagMonitor(pyboy_instance=pyboy)
    item_monitor.start_monitoring()

print("Game launched!")
if enable_monitoring:
    print("🔍 Item flag monitoring: ENABLED")
else:
    print("🔍 Item flag monitoring: DISABLED (use --monitor to enable)")
print("Controls: Arrow keys + Z(A) + X(B) + Enter(Start) + Space(Select)")
print("Terminal commands:")
print("  's' + Enter = Save state with auto-incrementing filename")
print("  'l <name>' + Enter = Load named state (e.g., 'l base')")
if enable_monitoring:
    print("  'r' + Enter = Reset monitoring baseline")
    print("  'f' + Enter = Show current non-zero flags")
print("  'q' + Enter = Quit")

# Make sure states directory exists
os.makedirs("roms", exist_ok=True)
save_count = 0
running = True

def check_input():
    global running, save_count
    while running:
        try:
            cmd = input().strip()
            
            if cmd.lower() == 'q':
                print("Exiting emulator.")
                running = False
                
            elif cmd.lower() == 's':
                # Auto-incrementing save with timestamp
                timestamp = datetime.now().strftime("%H%M%S")
                state_filename = f"roms/save_{save_count:02d}_{timestamp}.state"
                
                with open(state_filename, "wb") as f:
                    pyboy.save_state(f)
                
                print(f"✅ Saved state to: {state_filename}")
                save_count += 1
                
            elif cmd.lower().startswith('l '):
                # Load named state
                state_name = cmd[2:].strip()
                state_path = f"roms/{state_name}.state"
                
                try:
                    with open(state_path, "rb") as f:
                        pyboy.load_state(f)
                    print(f"✅ Loaded state: {state_path}")
                    # Reset monitoring baseline after loading state
                    if enable_monitoring and item_monitor:
                        item_monitor.update_flag_baseline()
                        print("📊 Monitoring baseline reset after state load")
                except FileNotFoundError:
                    print(f"❌ State not found: {state_path}")
            
            elif enable_monitoring and cmd.lower() == 'r':
                # Reset monitoring baseline
                if item_monitor:
                    item_monitor.update_flag_baseline()
                    print("📊 Monitoring baseline reset!")
                    
            elif enable_monitoring and cmd.lower() == 'f':
                # Show current flags
                if item_monitor:
                    item_monitor.print_current_flags()
                    
            else:
                base_cmds = "Commands: 's' to save, 'l <name>' to load, 'q' to quit"
                monitor_cmds = ", 'r' to reset baseline, 'f' to show flags" if enable_monitoring else ""
                print(base_cmds + monitor_cmds)
                
        except EOFError:
            break

input_thread = threading.Thread(target=check_input, daemon=True)
input_thread.start()

try:
    frame_count = 0
    while running:
        pyboy.tick()
        frame_count += 1
        
        # Check for item acquisitions if monitoring is enabled
        if enable_monitoring and item_monitor and frame_count % 30 == 0:
            acquisitions = item_monitor.check_flag_changes()
            if acquisitions:
                item_monitor.print_acquisitions(acquisitions)
        
        time.sleep(0.001)  # prevent CPU overuse
except KeyboardInterrupt:
    print("\nClosing game...")
finally:
    if enable_monitoring and item_monitor:
        print("📦 Final monitoring summary:")
        print(f"   Total items discovered: {len(item_monitor.discovered_items)}")
        for addr, val in item_monitor.discovered_items.items():
            print(f"   0x{addr:04X} = {val}")
    pyboy.stop()
