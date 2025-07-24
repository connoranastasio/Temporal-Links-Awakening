import os
from pathlib import Path
from datetime import datetime
from PIL import Image
import numpy as np

class FrameLogger:
    def __init__(self, log_root="temp_frames", diff_threshold=0.05):
        """
        :param diff_threshold: Percent of pixels that must differ to trigger a save (0.05 = 5%)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = Path(log_root) / f"Session_{timestamp}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.frame_count = 0
        self.last_frame = None
        self.diff_threshold = diff_threshold

    def log_if_different(self, current_frame_np):
        if self.last_frame is None:
            self._save_frame(current_frame_np)
        else:
            # Compare pixel-wise absolute difference
            diff = np.abs(current_frame_np.astype(np.int16) - self.last_frame.astype(np.int16))
            percent_changed = np.mean(diff > 10)  # Threshold: per-pixel RGB intensity change >10
            if percent_changed > self.diff_threshold:
                self._save_frame(current_frame_np)

    def _save_frame(self, frame):
        filename = self.session_dir / f"frame_{self.frame_count:06d}.png"
        Image.fromarray(frame).save(filename)
        self.last_frame = frame
        self.frame_count += 1
