#!/usr/bin/env python3
"""
Compare two save states to find RAM differences
Perfect for controlled input testing to discover specific RAM addresses
"""

from pyboy import PyBoy
import os

def compare_savestates(base_state_path, test_state_path, action_description=""):
    """
    Compare two save states and show which RAM addresses changed
    """
    rom_path = "roms/LinksAwakeningDX-Rev2.gbc"
    
    print(f"\n{'='*60}")
    print(f"COMPARING SAVE STATES")
    if action_description:
        print(f"Action: {action_description}")
    print(f"Base:   {base_state_path}")
    print(f"Test:   {test_state_path}")
    print(f"{'='*60}")
    
    # Load base state
    pyboy_base = PyBoy(rom_path, window="null", cgb=True)
    with open(base_state_path, "rb") as f:
        pyboy_base.load_state(f)
    
    # Load test state  
    pyboy_test = PyBoy(rom_path, window="null", cgb=True)
    with open(test_state_path, "rb") as f:
        pyboy_test.load_state(f)
    
    # Known position-related addresses to ignore
    position_addresses = {
        0xC008, 0xC009,  # Main X/Y position
        0xC00C, 0xC00D,  # Sub-pixel or offset X/Y
        0xFF98, 0xFF99, 0xFF9F, 0xFFA0,  # Position mirrors in High RAM
    }
    
    # Compare memory across key ranges
    memory_ranges = [
        (0x0000, 0x00FF, "Zero Page"),
        (0xC000, 0xC0FF, "Work RAM Low"), 
        (0xD000, 0xD0FF, "Work RAM Mid"),
        (0xDB00, 0xDBFF, "Work RAM High"),
        (0xFF80, 0xFFFE, "High RAM"),
    ]
    
    all_changes = []
    
    for start_addr, end_addr, range_name in memory_ranges:
        changes = []
        
        for addr in range(start_addr, end_addr + 1):
            # Skip known position addresses
            if addr in position_addresses:
                continue
                
            base_val = pyboy_base.memory[addr]
            test_val = pyboy_test.memory[addr]
            
            if base_val != test_val:
                changes.append({
                    'addr': addr,
                    'base': base_val,
                    'test': test_val,
                    'diff': test_val - base_val,
                    'range': range_name
                })
        
        if changes:
            print(f"\n🎯 {range_name} (0x{start_addr:04X}-0x{end_addr:04X}): {len(changes)} changes")
            for change in changes[:10]:  # Show first 10 per range
                addr = change['addr']
                print(f"  0x{addr:04X}: {change['base']:3d} -> {change['test']:3d} (Δ{change['diff']:+d})")
            if len(changes) > 10:
                print(f"  ... and {len(changes) - 10} more changes")
        
        all_changes.extend(changes)
    
    # Summary of most interesting changes
    if all_changes:
        print(f"\n📊 SUMMARY: {len(all_changes)} total changes found")
        
        # Show changes by magnitude
        significant_changes = [c for c in all_changes if abs(c['diff']) >= 1 and abs(c['diff']) <= 50]
        if significant_changes:
            print(f"\n🔍 Most likely candidates (small meaningful changes):")
            for change in significant_changes[:15]:
                addr = change['addr']
                print(f"  0x{addr:04X}: {change['base']:3d} -> {change['test']:3d} (Δ{change['diff']:+d}) [{change['range']}]")
    else:
        print("\n❌ No changes found - states might be identical")
    
    # Cleanup
    pyboy_base.stop()
    pyboy_test.stop()
    
    return all_changes

def compare_multiple_states():
    """
    Compare base.state with multiple test states if they exist
    """
    # Check for shield-specific base state first, then fall back to general base
    if os.path.exists("roms/shield_base.state"):
        base_path = "roms/shield_base.state"
    else:
        base_path = "roms/base.state"
    
    if not os.path.exists(base_path):
        print(f"❌ Base state not found: {base_path}")
        return
    
    print("🎯 Looking for test states to compare...")
    
    # Look for common test state names
    test_states = [
        ("roms/shield_base.state", "Shield Base (Before Getting Shield)"),
        ("roms/shield_acquired.state", "Shield Acquired"),
        ("roms/move_right.state", "Moved Right"),
        ("roms/move_left.state", "Moved Left"), 
        ("roms/move_up.state", "Moved Up"),
        ("roms/move_down.state", "Moved Down"),
        ("roms/use_a.state", "Used A Button"),
        ("roms/use_b.state", "Used B Button"),
    ]
    
    found_states = []
    for state_path, description in test_states:
        if os.path.exists(state_path):
            found_states.append((state_path, description))
    
    if not found_states:
        print("No test states found yet.")
        print("Create test states by:")
        print("1. Load base.state in PyBoy (press X)")
        print("2. Perform ONE specific action (e.g., move right 1 square)")
        print("3. Save as descriptive name (e.g., move_right.state)")
        print("4. Run this script again")
        return
    
    print(f"Found {len(found_states)} test states:")
    for state_path, description in found_states:
        print(f"  - {state_path} ({description})")
    
    # Compare each test state to base
    for state_path, description in found_states:
        compare_savestates(base_path, state_path, description)

if __name__ == "__main__":
    compare_multiple_states()