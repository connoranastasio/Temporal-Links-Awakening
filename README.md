# Temporal Link's Awakening

An AI that learns to play *The Legend of Zelda: Link’s Awakening DX* using deep reinforcement learning and the PyBoy emulator.

> **Disclaimer:** This project does not support or condone piracy. You must legally own *Link’s Awakening DX* and dump your own ROM. See the [Piracy Disclaimer](#-piracy-disclaimer) below for full details.


---

## ROM

- **Version:** The Legend of Zelda: Link’s Awakening DX (USA, Europe) (Rev 2)  
- **File Name:** `LinksAwakeningDX-Rev2.gbc`  
- **SHA-1 Hash:** `1c091225688d966928cc74336dbef2e07d12a47c`  
- **SHA-256 Hash:** `5dee5816ed9b46cfc4a2d94f275e555dd3c5080eca00ded975a41a881a6d4c06`

Place the ROM in the `roms/` directory. 

---

## Strategy

This project takes a RAM-focused approach to reinforcement learning, avoiding pixel-based vision models in favor of directly reading memory values from the emulator. Link's Awakening DX uses deterministic RNG and static RAM addresses, allowing us to locate the information we want reliably and quickly.

I believe this will lead to faster training and more interpretable progress by:
- Directly monitoring key game state (rupees, player health, room ID, inventory, etc etc) from RAM
- Assigning rewards for meaningful events like collecting rupees, exiting the house, or picking up the sword
- Avoiding the complexity and compute cost of CNN-based visual pipelines; visual pipelines offer unneeded variability, uncertainty, project size (thousands and thousands of auto generated images), and additional computation time/cost. RAM address mapping offers exact tangible progress we can rapdily tweak our model around.

PyBoy is used in SDL2 mode for manual gameplay, savestate generation, and later as a backend for automated training.

---

## Progress So Far

- Converted project to use **Link’s Awakening DX Rev 2.gbc** ROM  (project began using Link's Awakening Rev2.gb)
- Begun verifying known RAM addresses (`0x006D` for health, `0x006F` for rupees, etc) against community sources  
- Built a clean savestate to use as the reproducible starting point  
- Implemented a manual play+RAM-dump script  
- Switched from nonexistent `get_window()` function to PyBoy's native input flow  
- Designed initial reward function focused on early-game progress (rupees, sword, escape)  
- Created training environment using Gym-compatible `LinkEnv` wrapper

---

## Next Steps

- Map out additional RAM flags for sword pickup, dungeon entry, and boss progress  
- Iterate on reward shaping strategy (sparse → dense)  
- Integrate PPO/other agents with stable-baselines3 
- Add training logs and optional RAM visualizer/debugger  
- Evaluate learned policies on real gameplay scenarios
- Create install/setup guide for others wishing to contribrute (please do!)
- Polish RAM diffing script and process, write out instructions

---

## RAM Diffing for Discovery

While there are many common RAM addresses documented online, the majority of specific addresses is not currently known. To uncover new RAM addresses related to story flags, items, and progress, we also use **savestate and battery save diffing**:

- Compare `.state` or `.sav` files from before and after specific in-game events
- Identify which memory addresses change
- Use this to track event flags, chest states, dungeon progress, etc.

This technique helps us expand the reward function and automate quest tracking, as needed. As we progress further with building a more reliable model, this will greatly assist with model fine-tuning. It also complements direct memory scanning and allows for fast, repeatable reverse engineering of game mechanics.

---

## Piracy Disclaimer

**Absolutely no piracy is allowed or tolerated in this project.**

This repository exists for research and educational purposes only. You must legally own *The Legend of Zelda: Link’s Awakening DX (Rev 2)* and **create your own ROM dump from your personal copy** of the game. No ROMs, BIOS files, copyrighted assets, or proprietary Nintendo content may be uploaded, linked, or shared.

Any attempt to solicit or distribute copyrighted material — including in issues, discussions, pull requests, or external links — will result in immediate removal and may lead to a permanent ban.

**All contributors are expected to respect copyright law, Nintendo’s IP rights, and the ethical standards of open-source collaboration.**

This policy is non-negotiable and strictly enforced.


## Credits

This project builds on the work of several incredible open-source creators, libraries, and communities:

This project builds on the work of several incredible open-source creators and tools:

- [**PyBoy**](https://github.com/Baekalfen/PyBoy) (MIT License) – Game Boy emulator in Python by [@Baekalfen](https://github.com/Baekalfen), which makes reinforcement learning on GB/GBC games possible.
- [**PokemonRedExperiments**](https://github.com/PWhiddy/PokemonRedExperiments/tree/master) (MIT License) – By [@PWhiddy](https://github.com/PWhiddy). While this project is not directly based on any of their code, their project offered inspiration and a clear example of successful emulator-based reinforcement learning in action. It's also awesome in general, definitely check it out.
- [**Artemis251’s Zelda Hacking Site**](http://artemis251.fobby.net/zelda/index.php) – A valuable resource for RAM maps and reverse-engineering *Link’s Awakening DX*, helping guide our memory-based reward system. This was the main jumping-off point for implementing the initial reward-based training and searching for additional RAM addresses myself.
- [**stable-baselines3**](https://github.com/DLR-RM/stable-baselines3) (MIT License) – Deep reinforcement learning algorithms.
- [**Gymnasium**](https://github.com/Farama-Foundation/Gymnasium) (MIT License) – Gym-compatible RL environment interface.
- [**NumPy**](https://github.com/numpy/numpy) (BSD 3-Clause License) – Array manipulation.
- [**PyTorch**](https://pytorch.org/) (BSD-style License) – Neural network training backend.
- [**Pillow**](https://github.com/python-pillow/Pillow) (HPND License) – Image handling library used for screenshots and screen capture.
- [**OpenCV**](https://github.com/opencv/opencv-python) (Apache 2.0 License) – Image utilities used for optional image processing.

Huge thanks to the authors and maintainers of these tools for enabling research and experimentation.
Special thanks to the broader Game Boy reverse-engineering community for their thorough documentation and long-standing contributions to game hacking and modding.

## License

This project is for research and educational purposes only. All original code is MIT-licensed; libraries used have their respective licenses isted above in the credits. All game assets and ROMs remain property of their respective copyright holders.
