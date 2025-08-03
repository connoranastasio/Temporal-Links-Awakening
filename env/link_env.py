import gymnasium as gym
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from gymnasium.spaces import Box, Discrete
import time
import os


class LinkEnv(gym.Env):
    """
    Reinforcement learning environment for Link's Awakening DX using PyBoy.
    """

    def __init__(self, render=False):
        super().__init__()

        self.render_mode = "rgb_array" if render else None
        self.render_enabled = render

        window_arg = "SDL2" if render else "null"
        self.pyboy = PyBoy("roms/LinksAwakeningDX-Rev2.gbc", window=window_arg, cgb=True, sound=False, sound_emulated=False)
        # Maximum stable speeds for fast training
        speed = 15 if render else 30
        self.pyboy.set_emulation_speed(speed)
        
        # Track state for reward calculation
        self.visited_positions = set()
        self.previous_flags = {}
        self.previous_health = None
        self.previous_x = None
        self.previous_y = None
        
        # Item flag monitoring setup
        self.FLAG_START = 0xDB00
        self.FLAG_END = 0xDBFF
        self.flag_range = range(self.FLAG_START, self.FLAG_END + 1)
        self.discovered_items = {}
        self.state_save_count = 0
        
        # Equipment slot addresses to ignore (based on Data Crystal)
        self.EQUIPMENT_SLOTS = {0xDB00, 0xDB01}  # Currently held items A/B slots
        
        # Track major milestones with step counts
        self.left_house = False
        self.shield_equipped = False
        self.previous_shield_equipped = False
        self.step_count = 0
        self.milestones = {}  # Track when major events happen
        
        # Map/area transition tracking (D700-D79B range from Data Crystal)
        self.discovered_map_values = set()  # Track unique map values seen
        
        # Ensure states directory exists
        os.makedirs("roms/training_states", exist_ok=True)

        self.buttons = [
            (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
            (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
            (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
            (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
            (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
            (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B),
            (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START)
        ]
        self.action_space = Discrete(len(self.buttons))
        self.observation_space = Box(low=0, high=255, shape=(144, 160, 3), dtype=np.uint8)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        self.pyboy.stop()
        window_arg = "SDL2" if self.render_enabled else "null"
        self.pyboy = PyBoy("roms/LinksAwakeningDX-Rev2.gbc", window=window_arg, cgb=True, sound=False, sound_emulated=False)
        # Maximum stable speeds for fast training
        speed = 15 if self.render_enabled else 30
        self.pyboy.set_emulation_speed(speed)

        with open("roms/base.state", "rb") as f:
            self.pyboy.load_state(f)

        # Reset tracking variables
        self.visited_positions = set()
        self.previous_flags = {}
        self.previous_health = None
        self.previous_x = None
        self.previous_y = None
        self.discovered_items = {}
        
        # Initialize baseline state
        self._update_baseline()

        obs = self._get_obs()
        info = {}
        return obs, info

    def step(self, action_idx):
        # Increment step counter
        self.step_count += 1
        
        press_event, release_event = self.buttons[action_idx]
        self.pyboy.send_input(press_event)
        self.pyboy.tick()
        self.pyboy.send_input(release_event)

        for _ in range(4):
            self.pyboy.tick()

        obs = self._get_obs()
        reward = self._calculate_reward()
        terminated = False
        truncated = False
        info = {"milestones": self.milestones.copy()}  # Include milestones in info

        return obs, reward, terminated, truncated, info

    def render(self):
        return np.array(self.pyboy.screen.image)

    def close(self):
        self.pyboy.stop()

    def _get_obs(self):
        return np.array(self.pyboy.screen.image)[:, :, :3]

    def _update_baseline(self):
        """Update baseline for position and flags"""
        # Initialize position tracking
        self.previous_x = self.pyboy.memory[0xD500]  # Link's X position
        self.previous_y = self.pyboy.memory[0xD501]  # Link's Y position
        self.previous_health = self.pyboy.memory[0xDB5A]  # Current health
        
        # Initialize flag baseline
        for addr in self.flag_range:
            self.previous_flags[addr] = self.pyboy.memory[addr]
    
    def _check_item_flags(self):
        """Check for new item acquisitions and save states"""
        new_acquisitions = []
        
        for addr in self.flag_range:
            old_val = self.previous_flags[addr]
            new_val = self.pyboy.memory[addr]
            
            # Flag changed from 0 to 1 AND we haven't rewarded this address before AND it's not an equipment slot
            if old_val == 0 and new_val == 1 and addr not in self.discovered_items and addr not in self.EQUIPMENT_SLOTS:
                new_acquisitions.append({
                    'addr': addr,
                    'old': old_val,
                    'new': new_val
                })
                self.discovered_items[addr] = new_val
                
                # Track milestone
                self.milestones[f"item_0x{addr:04X}"] = self.step_count
                
                # Save state when item is acquired
                timestamp = time.strftime("%H%M%S")
                state_filename = f"roms/training_states/item_{addr:04X}_{self.state_save_count:03d}_{timestamp}.state"
                with open(state_filename, "wb") as f:
                    self.pyboy.save_state(f)
                print(f"🎉 ITEM ACQUIRED! Step {self.step_count}, Address 0x{addr:04X}: {old_val} → {new_val} | Saved: {state_filename}")
                self.state_save_count += 1
                
            # Update for next check
            self.previous_flags[addr] = new_val
        
        return len(new_acquisitions)
    
    def _calculate_reward(self):
        reward = 0.0
        
        # Get current state
        current_x = self.pyboy.memory[0xD500]
        current_y = self.pyboy.memory[0xD501]
        current_health = self.pyboy.memory[0xDB5A]
        
        # Exploration reward - new positions
        position = (current_x, current_y)
        if position not in self.visited_positions:
            self.visited_positions.add(position)
            reward += 1.0  # Small reward for exploration
        
        # Big reward for leaving the house (first time only)
        # Log coordinates to understand the house boundaries
        if not self.left_house and (current_x < 70 or current_x > 90 or current_y < 70 or current_y > 90):
            self.left_house = True
            self.milestones["left_house"] = self.step_count
            reward += 50.0  # Huge one-time reward for leaving house
            print(f"🏠➡️ LEFT THE HOUSE! Step {self.step_count}, Position: ({current_x}, {current_y}) - One-time +50 reward!")
            
            # Save state when leaving house for analysis
            timestamp = time.strftime("%H%M%S")
            state_filename = f"roms/training_states/left_house_{current_x}_{current_y}_{timestamp}.state"
            with open(state_filename, "wb") as f:
                self.pyboy.save_state(f)
            print(f"💾 Saved house exit state: {state_filename}")
        
        # Area/room transition rewards (use only a few key map addresses, not the entire range)
        # Focus on main map ID address instead of entire range
        main_map_id = self.pyboy.memory[0xD700]  # Main map identifier
        map_key = f"map_{main_map_id:02X}"
        
        if map_key not in self.discovered_map_values:
            self.discovered_map_values.add(map_key)
            self.milestones[f"area_{map_key}"] = self.step_count
            reward += 25.0  # Big reward for actual area transitions
            print(f"🗺️ NEW AREA! Step {self.step_count}, Map ID = {main_map_id} | Reward +25")
        
        # Stronger directional rewards toward beach/sword (prioritize over random exploration)
        if self.previous_y is not None:
            if current_y > self.previous_y:  # Moving south (toward beach)
                reward += 0.5  # Stronger southward bonus
            if current_x > self.previous_x:  # Moving east (toward beach)  
                reward += 0.3  # Good eastward bonus
            # Small penalty for moving away from beach
            if current_y < self.previous_y:  # Moving north (away from beach)
                reward -= 0.1  # Discourage going away from beach
        
        # Item acquisition reward
        item_acquisitions = self._check_item_flags()
        reward += item_acquisitions * 10.0  # Big reward for items
        
        # Check shield equipment status (look for specific shield value, not just any value)
        # Based on Data Crystal: 0xDB44 is shield level, or check for shield item ID in slots
        shield_value_a = self.pyboy.memory[0xDB00]  # A slot item
        shield_value_b = self.pyboy.memory[0xDB01]  # B slot item
        
        # Shield item ID might be a specific value (need to determine empirically)
        # For now, let's just track when shield level changes at 0xDB44
        shield_level = self.pyboy.memory[0xDB44]  # Shield level from Data Crystal
        
        # Only track shield level changes, not item slot shuffling
        if hasattr(self, 'previous_shield_level'):
            if shield_level > self.previous_shield_level and not self.shield_equipped:
                # Shield level increased (got shield)
                self.shield_equipped = True
                self.milestones["shield_equipped"] = self.step_count
                reward += 15.0
                print(f"🛡️ SHIELD ACQUIRED! Step {self.step_count}, Shield level: {shield_level} | Bonus: +15")
        
        self.previous_shield_level = shield_level
        
        # Reduced health loss penalty (was -2.0, now -0.5)
        if self.previous_health is not None and current_health < self.previous_health:
            health_lost = self.previous_health - current_health
            reward -= health_lost * 0.5  # Reduced penalty for exploration
        
        # Death penalty
        if current_health == 0:
            reward -= 50.0  # Big penalty for dying
        
        # Update previous values
        self.previous_x = current_x
        self.previous_y = current_y
        self.previous_health = current_health
        
        return reward
