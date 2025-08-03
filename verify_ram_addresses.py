#!/usr/bin/env python3
"""
RAM address verification and discovery from scratch
Only uses .gbc ROM and related files - ignores all .gb files
"""

from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
from collections import defaultdict

class RAMVerifier:
    def __init__(self):
        # Only use GBC ROM and state - use the moveable savestate
        self.rom_path = "roms/LinksAwakeningDX-Rev2.gbc"
        self.state_path = "roms/LinksAwakeningDX-Rev2-moveable.gbc.state"
        
        self.pyboy = None
        self.memory = None
        
    def verify_files(self):
        """Verify GBC ROM and state files exist and work"""
        try:
            print(f"Testing {self.rom_path}...")
            pyboy = PyBoy(self.rom_path, window="null", cgb=True)
            
            try:
                with open(self.state_path, "rb") as f:
                    pyboy.load_state(f)
                print(f"✓ {self.rom_path} and {self.state_path} work!")
                pyboy.stop()
                return True
            except FileNotFoundError:
                print(f"✗ State file {self.state_path} not found")
                pyboy.stop()
                return False
            except Exception as e:
                print(f"✗ State loading failed: {e}")
                pyboy.stop()
                return False
                
        except FileNotFoundError:
            print(f"✗ ROM file {self.rom_path} not found")
            return False
        except Exception as e:
            print(f"✗ ROM loading failed: {e}")
            return False
    
    def setup_emulator(self):
        """Setup emulator with GBC ROM"""
        self.pyboy = PyBoy(self.rom_path, window="SDL2", cgb=True)
        self.pyboy.set_emulation_speed(1)
        
        with open(self.state_path, "rb") as f:
            self.pyboy.load_state(f)
        
        self.memory = self.pyboy.memory
        print(f"Emulator ready with {self.rom_path}")
        
    def scan_memory_range(self, start_addr, end_addr, action_name, action_func):
        """Scan a range of memory addresses before and after an action"""
        print(f"\nScanning 0x{start_addr:04X}-0x{end_addr:04X} for '{action_name}'")
        
        # Reset to initial state
        with open(self.state_path, "rb") as f:
            self.pyboy.load_state(f)
        
        # Wait for stability
        for _ in range(60):
            self.pyboy.tick()
        
        # Take before snapshot
        before = {}
        for addr in range(start_addr, end_addr + 1):
            before[addr] = self.memory[addr]
        
        # Perform action
        print(f"Performing action: {action_name}")
        action_func()
        
        # Wait for effects
        for _ in range(120):
            self.pyboy.tick()
        
        # Take after snapshot
        changes = []
        for addr in range(start_addr, end_addr + 1):
            after_val = self.memory[addr]
            if before[addr] != after_val:
                changes.append({
                    'addr': addr,
                    'before': before[addr], 
                    'after': after_val,
                    'diff': after_val - before[addr]
                })
        
        print(f"Found {len(changes)} changes:")
        for change in changes[:10]:  # Show first 10
            addr = change['addr']
            print(f"  0x{addr:04X}: {change['before']:3d} -> {change['after']:3d} (Δ{change['diff']:+d})")
        
        return changes
    
    def test_movement(self):
        """Test if movement changes any RAM addresses"""
        
        def move_right_extended():
            """Move right for a longer period"""
            for _ in range(60):  # 1 second of movement
                self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
                self.pyboy.tick()
        
        def move_down_extended():
            """Move down for a longer period"""
            for _ in range(60):
                self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN) 
                self.pyboy.tick()
        
        # Test multiple memory ranges
        ranges_to_test = [
            (0x0000, 0x00FF, "Zero Page"),
            (0xC000, 0xC0FF, "Work RAM Low"),
            (0xD000, 0xD0FF, "Work RAM Mid"),
            (0xDB00, 0xDBFF, "Work RAM High"),
            (0xFF80, 0xFFFE, "High RAM"),
        ]
        
        all_changes = {}
        
        for start, end, name in ranges_to_test:
            print(f"\n{'='*50}")
            print(f"Testing {name} (0x{start:04X}-0x{end:04X})")
            print(f"{'='*50}")
            
            changes_right = self.scan_memory_range(start, end, "Move Right Extended", move_right_extended)
            changes_down = self.scan_memory_range(start, end, "Move Down Extended", move_down_extended)
            
            all_changes[f"{name}_right"] = changes_right
            all_changes[f"{name}_down"] = changes_down
        
        return all_changes
    
    def find_position_addresses(self):
        """Specifically look for player position addresses"""
        print("\n" + "="*60)
        print("FOCUSED SEARCH: Looking for Player Position Addresses")
        print("="*60)
        
        def move_right_precise():
            # Single precise movement
            self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
            for _ in range(30):  # Hold for half second
                self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
        
        # Focus on most likely ranges for position data
        position_ranges = [
            (0xD100, 0xD110, "Classic Position Range"),
            (0x00A0, 0x00B0, "Alt Position Range"),
            (0xDB90, 0xDBA0, "Stats Area"),
        ]
        
        for start, end, name in position_ranges:
            changes = self.scan_memory_range(start, end, f"Precise Right Move ({name})", move_right_precise)
            if changes:
                print(f"\n🎯 FOUND POSITION CANDIDATES in {name}:")
                for change in changes:
                    print(f"   0x{change['addr']:04X} is likely X position (changed by {change['diff']})")
    
    def cleanup(self):
        if self.pyboy:
            self.pyboy.stop()

def main():
    verifier = RAMVerifier()
    
    # Step 1: Verify GBC files work
    if not verifier.verify_files():
        print("❌ GBC ROM/state files not working!")
        print("Make sure you have:")
        print("  - roms/LinksAwakeningDX-Rev2.gbc")
        print("  - roms/LinksAwakeningDX-Rev2.gbc.state")
        return
    
    try:
        # Step 2: Setup emulator
        verifier.setup_emulator()
        
        # Step 3: Test basic movement to find ANY changing addresses
        print("\n🔍 Phase 1: Wide scan for movement-related changes")
        movement_changes = verifier.test_movement()
        
        # Step 4: Focused search for position
        print("\n🎯 Phase 2: Focused search for position addresses")
        verifier.find_position_addresses()
        
        print("\n✅ Discovery complete!")
        print("Check the output above for promising addresses to investigate further.")
        
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        import traceback
        traceback.print_exc()
    finally:
        verifier.cleanup()

if __name__ == "__main__":
    main()