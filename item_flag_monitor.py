#!/usr/bin/env python3
"""
Real-time item flag monitor for Link's Awakening DX
Watches 0xDB00-0xDBFF region and alerts when flags change from 0→1
"""

from pyboy import PyBoy
import threading
import time
import os

class ItemFlagMonitor:
    def __init__(self, pyboy_instance=None):
        self.rom_path = "roms/LinksAwakeningDX-Rev2.gbc"
        self.pyboy = pyboy_instance  # Use external instance if provided
        self.running = True
        self.owns_pyboy = pyboy_instance is None  # Track if we manage PyBoy lifecycle
        
        # Item flag region to monitor
        self.FLAG_START = 0xDB00
        self.FLAG_END = 0xDBFF
        self.flag_range = range(self.FLAG_START, self.FLAG_END + 1)
        
        # Store previous flag states
        self.previous_flags = {}
        self.discovered_items = {}
        
    def setup_emulator(self):
        """Setup PyBoy with a base state (only if we own the instance)"""
        if self.pyboy is None:
            self.pyboy = PyBoy(self.rom_path, window="SDL2", cgb=True)
            self.pyboy.set_emulation_speed(1)
            
            # Try to load a base state if available
            if os.path.exists("roms/base.state"):
                with open("roms/base.state", "rb") as f:
                    self.pyboy.load_state(f)
                print("✅ Loaded base.state")
            else:
                print("⚠️ No base.state found, starting from ROM boot")
        
        # Initialize previous flags regardless of PyBoy source
        self.update_flag_baseline()
        
    def update_flag_baseline(self):
        """Update the baseline of all flags"""
        for addr in self.flag_range:
            self.previous_flags[addr] = self.pyboy.memory[addr]
        print(f"📊 Monitoring {len(self.flag_range)} addresses from 0x{self.FLAG_START:04X} to 0x{self.FLAG_END:04X}")
    
    def check_flag_changes(self):
        """Check for any flags that changed from 0→1"""
        new_acquisitions = []
        
        for addr in self.flag_range:
            old_val = self.previous_flags[addr]
            new_val = self.pyboy.memory[addr]
            
            # Flag changed from 0 to 1 = item acquired!
            if old_val == 0 and new_val == 1:
                new_acquisitions.append({
                    'addr': addr,
                    'old': old_val,
                    'new': new_val
                })
                self.discovered_items[addr] = new_val
                
            # Update for next check
            self.previous_flags[addr] = new_val
        
        return new_acquisitions
    
    def print_acquisitions(self, acquisitions):
        """Print newly acquired items"""
        for item in acquisitions:
            addr = item['addr']
            print(f"🎉 ITEM ACQUIRED! Address 0x{addr:04X}: {item['old']} → {item['new']}")
        
        if acquisitions:
            print(f"📦 Total items discovered: {len(self.discovered_items)}")
    
    def print_current_flags(self):
        """Print current non-zero flags for debugging"""
        non_zero = []
        for addr in self.flag_range:
            val = self.pyboy.memory[addr]
            if val != 0:
                non_zero.append(f"0x{addr:04X}={val}")
        
        if non_zero:
            print(f"🔍 Non-zero flags: {', '.join(non_zero[:10])}" + 
                  (f" (+{len(non_zero)-10} more)" if len(non_zero) > 10 else ""))
    
    def input_handler(self):
        """Handle user input commands"""
        print("\nCommands:")
        print("  'r' + Enter = Reset baseline (use after loading a different state)")
        print("  'f' + Enter = Show current non-zero flags")
        print("  's' + Enter = Save current state as item_monitor.state")
        print("  'q' + Enter = Quit")
        
        while self.running:
            try:
                cmd = input().strip().lower()
                
                if cmd == 'q':
                    print("Exiting monitor...")
                    self.running = False
                    
                elif cmd == 'r':
                    self.update_flag_baseline()
                    print("📊 Baseline reset!")
                    
                elif cmd == 'f':
                    self.print_current_flags()
                    
                elif cmd == 's':
                    timestamp = time.strftime("%H%M%S")
                    state_path = f"roms/item_monitor_{timestamp}.state"
                    with open(state_path, "wb") as f:
                        self.pyboy.save_state(f)
                    print(f"💾 Saved state: {state_path}")
                    
                else:
                    print("Unknown command. Use 'r', 'f', 's', or 'q'")
                    
            except EOFError:
                break
    
    def run(self):
        """Main monitoring loop (only when running standalone)"""
        print("🎮 Item Flag Monitor for Link's Awakening DX")
        print("="*50)
        
        self.setup_emulator()
        
        # Start input thread
        input_thread = threading.Thread(target=self.input_handler, daemon=True)
        input_thread.start()
        
        print("\n🔍 Monitoring for item acquisitions...")
        print("Go collect items in the game and watch for alerts!")
        
        try:
            frame_count = 0
            while self.running:
                self.pyboy.tick()
                frame_count += 1
                
                # Check for flag changes every 30 frames (half second)
                if frame_count % 30 == 0:
                    acquisitions = self.check_flag_changes()
                    if acquisitions:
                        self.print_acquisitions(acquisitions)
                
                time.sleep(0.001)  # Prevent CPU overuse
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            # Only stop PyBoy if we own it
            if self.owns_pyboy and self.pyboy:
                self.pyboy.stop()
            print("📦 Final summary:")
            print(f"   Total items discovered: {len(self.discovered_items)}")
            for addr, val in self.discovered_items.items():
                print(f"   0x{addr:04X} = {val}")
    
    def start_monitoring(self):
        """Initialize monitoring for external PyBoy instance"""
        if self.pyboy is None:
            raise ValueError("No PyBoy instance available for monitoring")
        self.update_flag_baseline()
        print(f"📊 Monitoring {len(self.flag_range)} addresses from 0x{self.FLAG_START:04X} to 0x{self.FLAG_END:04X}")

def main():
    monitor = ItemFlagMonitor()
    monitor.run()

if __name__ == "__main__":
    main()