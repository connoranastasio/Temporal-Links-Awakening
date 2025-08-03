#!/usr/bin/env python3
"""
Save state manager - automatically backs up and renames PyBoy save states
"""

import os
import shutil
from datetime import datetime

class StateManager:
    def __init__(self):
        self.rom_path = "roms/LinksAwakeningDX-Rev2.gbc"
        self.default_state = "roms/LinksAwakeningDX-Rev2.gbc.state"
        self.backup_dir = "roms/"
        
    def backup_current_state(self, name):
        """Backup current state with a descriptive name"""
        if not os.path.exists(self.default_state):
            print(f"❌ No current state found at {self.default_state}")
            return False
        
        backup_path = f"{self.backup_dir}{name}.state"
        shutil.copy2(self.default_state, backup_path)
        print(f"✅ Saved current state as: {backup_path}")
        return True
    
    def load_state(self, name):
        """Load a named state back to the default location"""
        source_path = f"{self.backup_dir}{name}.state"
        
        if not os.path.exists(source_path):
            print(f"❌ State not found: {source_path}")
            return False
        
        shutil.copy2(source_path, self.default_state)
        print(f"✅ Loaded {source_path} as current state")
        return True
    
    def list_states(self):
        """List all saved states"""
        states = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.state') and file != 'LinksAwakeningDX-Rev2.gbc.state':
                # Remove .state extension for display
                name = file[:-6]
                states.append(name)
        
        if states:
            print("📁 Available states:")
            for i, state in enumerate(states, 1):
                print(f"  {i}. {state}")
        else:
            print("📁 No saved states found")
        
        return states
    
    def quick_save(self):
        """Quick save with timestamp"""
        timestamp = datetime.now().strftime("%H%M%S")
        name = f"quick_save_{timestamp}"
        return self.backup_current_state(name)

def main():
    manager = StateManager()
    
    if len(os.sys.argv) < 2:
        print("🎮 PyBoy State Manager")
        print("\nUsage:")
        print("  python state_manager.py save <name>     # Save current state with name")
        print("  python state_manager.py load <name>     # Load named state")
        print("  python state_manager.py list            # List all states")
        print("  python state_manager.py quick           # Quick save with timestamp")
        print("\nExamples:")
        print("  python state_manager.py save base")
        print("  python state_manager.py save move_right")
        print("  python state_manager.py load base")
        return
    
    command = os.sys.argv[1].lower()
    
    if command == "save" and len(os.sys.argv) >= 3:
        name = os.sys.argv[2]
        manager.backup_current_state(name)
    
    elif command == "load" and len(os.sys.argv) >= 3:
        name = os.sys.argv[2]
        manager.load_state(name)
    
    elif command == "list":
        manager.list_states()
    
    elif command == "quick":
        manager.quick_save()
    
    else:
        print("❌ Unknown command or missing arguments")
        main()

if __name__ == "__main__":
    main()