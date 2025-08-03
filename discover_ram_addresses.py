#!/usr/bin/env python3
"""
Efficient RAM address discovery for Link's Awakening DX
Uses event-driven monitoring instead of savestate diffing
"""

from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
from collections import defaultdict

class EfficientRAMDiscovery:
    def __init__(self, rom_path, state_path):
        self.pyboy = PyBoy(rom_path, window="SDL2", cgb=True)
        self.pyboy.set_emulation_speed(1)  # Normal speed for visualization
        
        # Load starting state
        with open(state_path, "rb") as f:
            self.pyboy.load_state(f)
        
        self.memory = self.pyboy.memory
        self.baseline = {}
        self.candidates = defaultdict(list)
        
        # Priority ranges based on typical Zelda memory layout
        self.ranges = {
            'player_stats': (0x0050, 0x007F),
            'position': (0x0080, 0x00AF), 
            'inventory': (0x00B0, 0x00DF),
            'flags': (0x00E0, 0x01FF),
            'dungeon_state': (0x0200, 0x02FF),
        }
    
    def take_baseline(self, frames=180):
        """Establish baseline - what changes during normal gameplay"""
        print("Taking baseline (normal gameplay)...")
        self.baseline = {}
        
        for addr in range(0x0000, 0x0300):  # Common ranges
            self.baseline[addr] = self.memory[addr]
        
        # Run for a few seconds to see normal fluctuations
        for _ in range(frames):
            self.pyboy.tick()
        
        print("Baseline complete")
    
    def test_action(self, action_name, action_func, post_frames=120):
        """Test a specific action and find RAM addresses that change"""
        print(f"\nTesting action: {action_name}")
        
        # Reset to baseline state
        with open("roms/LinksAwakeningDX-Rev2.gbc.state", "rb") as f:
            self.pyboy.load_state(f)
        
        # Wait a moment to stabilize
        for _ in range(30):
            self.pyboy.tick()
        
        # Take pre-action snapshot
        pre_snapshot = {}
        for addr in range(0x0000, 0x0300):
            pre_snapshot[addr] = self.memory[addr]
        
        # Perform action
        action_func()
        
        # Wait for effects to register
        for _ in range(post_frames):
            self.pyboy.tick()
        
        # Take post-action snapshot
        changes = []
        for addr in range(0x0000, 0x0300):
            post_value = self.memory[addr]
            if pre_snapshot[addr] != post_value:
                changes.append({
                    'address': addr,
                    'before': pre_snapshot[addr],
                    'after': post_value,
                    'diff': post_value - pre_snapshot[addr],
                    'action': action_name
                })
        
        # Filter meaningful changes (not just random fluctuations)
        meaningful_changes = [c for c in changes if abs(c['diff']) > 0]
        
        print(f"Found {len(meaningful_changes)} changes for {action_name}")
        for change in meaningful_changes[:10]:  # Show first 10
            print(f"  0x{change['address']:04X}: {change['before']} -> {change['after']} (Δ{change['diff']:+d})")
        
        return meaningful_changes
    
    def discover_common_addresses(self):
        """Discover addresses for common gameplay events"""
        
        results = {}
        
        # Test moving in different directions
        def move_right():
            for _ in range(30):
                self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
                self.pyboy.tick()
        
        def move_up():
            for _ in range(30):
                self.pyboy.send_input(WindowEvent.PRESS_ARROW_UP)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_UP)
                self.pyboy.tick()
        
        def use_a_button():
            for _ in range(5):
                self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
                for _ in range(10):
                    self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
                for _ in range(10):
                    self.pyboy.tick()
        
        def use_b_button():
            for _ in range(5):
                self.pyboy.send_input(WindowEvent.PRESS_BUTTON_B)
                for _ in range(10):
                    self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_B)
                for _ in range(10):
                    self.pyboy.tick()
        
        # Run tests
        results['move_right'] = self.test_action("Move Right", move_right)
        results['move_up'] = self.test_action("Move Up", move_up)
        results['use_a'] = self.test_action("Use A Button", use_a_button)
        results['use_b'] = self.test_action("Use B Button", use_b_button)
        
        return results
    
    def analyze_results(self, results):
        """Analyze results to identify the most promising addresses"""
        
        # Count how often each address changes across different actions
        address_frequency = defaultdict(int)
        address_details = defaultdict(list)
        
        for action, changes in results.items():
            for change in changes:
                addr = change['address']
                address_frequency[addr] += 1
                address_details[addr].append(change)
        
        print("\n=== ANALYSIS ===")
        print("Most frequently changing addresses:")
        
        # Sort by frequency
        sorted_addresses = sorted(address_frequency.items(), key=lambda x: x[1], reverse=True)
        
        for addr, freq in sorted_addresses[:20]:  # Top 20
            print(f"\n0x{addr:04X} (changed in {freq} actions):")
            for detail in address_details[addr][:3]:  # Show first 3 changes
                print(f"  {detail['action']}: {detail['before']} -> {detail['after']}")
    
    def cleanup(self):
        self.pyboy.stop()

def main():
    discovery = EfficientRAMDiscovery(
        "roms/LinksAwakeningDX-Rev2.gbc",
        "roms/LinksAwakeningDX-Rev2.gbc.state"
    )
    
    try:
        discovery.take_baseline()
        results = discovery.discover_common_addresses()
        discovery.analyze_results(results)
        
        print("\nDiscovery complete! Check the analysis above for promising addresses.")
        
    finally:
        discovery.cleanup()

if __name__ == "__main__":
    main()