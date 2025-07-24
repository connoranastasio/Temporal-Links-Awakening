import gymnasium as gym
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from gymnasium.spaces import Box, Discrete


class LinkEnv(gym.Env):
    """
    Reinforcement learning environment for Link's Awakening using PyBoy.
    """

    def __init__(self, render=False):
        super().__init__()

        self.render_mode = "rgb_array" if render else None
        self.render_enabled = render

        window_arg = "SDL2" if render else "null"
        self.pyboy = PyBoy("roms/LinksAwakening-Rev2.gb", window=window_arg)
        self.pyboy.set_emulation_speed(0)

        self.buttons = [
            (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
            (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
            (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
            (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
            (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
            (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B)
        ]
        self.action_space = Discrete(len(self.buttons))
        self.observation_space = Box(low=0, high=255, shape=(144, 160, 3), dtype=np.uint8)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        self.pyboy.stop()
        self.pyboy = PyBoy("roms/LinksAwakening-Rev2.gb", window="null")
        self.pyboy.set_emulation_speed(0)

        with open("roms/LinksAwakening-Rev2.gb.state", "rb") as f:
            self.pyboy.load_state(f)

        obs = self._get_obs()
        info = {}
        return obs, info

    def step(self, action_idx):
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
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self):
        return np.array(self.pyboy.screen.image)

    def close(self):
        self.pyboy.stop()

    def _get_obs(self):
        return np.array(self.pyboy.screen.image)[:, :, :3]

    def _calculate_reward(self):
        return 0.0
