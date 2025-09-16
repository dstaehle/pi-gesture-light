# gesture_control.py
# Utilities for extracting hand features and mapping them into gestures.

import math
import time
from collections import deque

# ---------- Utility ----------
def dist(a, b):
    """Euclidean distance between two MediaPipe landmarks."""
    return math.hypot(a.x - b.x, a.y - b.y)

# ---------- Feature extraction ----------
class HandFeatures:
    """
    Wraps MediaPipe landmarks to compute useful features:
    - openness: how "open" the hand is (0 = fist, ~0.6 = open palm)
    - pinch_ratio: thumb-index distance normalized to hand size
    """
    def __init__(self, lm):
        self.lm = lm
        self.wrist = lm[0]
        self.index_mcp = lm[5]
        self.index_tip = lm[8]
        self.thumb_tip = lm[4]
        self.middle_tip = lm[12]
        self.ring_tip = lm[16]
        self.pinky_tip = lm[20]
        self.hand_scale = dist(self.wrist, self.index_mcp) + 1e-6  # avoid div by 0

    @property
    def pinch_ratio(self):
        return dist(self.index_tip, self.thumb_tip) / self.hand_scale

    @property
    def openness(self):
        tips = [self.index_tip, self.middle_tip, self.ring_tip, self.pinky_tip]
        d = sum(dist(t, self.wrist) for t in tips) / (4*self.hand_scale)
        return d  # ~0.3 fist, ~0.6+ open palm

# ---------- Gesture state machine ----------
class GestureStateMachine:
    """
    Maps features into discrete gestures ("ON", "OFF") or continuous level set.
    Includes debounce, hysteresis, and output smoothing.
    """
    def __init__(self):
        self.mode = "IDLE"      # IDLE or SETLEVEL
        self.last_discrete = None
        self._open_stable = 0
        self._fist_stable = 0
        self._cooldown_until = 0
        self.target_level = 0.7     # default when turning ON
        self.filtered_level = 0.0
        self.ramp_per_sec = 0.8     # max change per second

        # thresholds (tune for your setup)
        self.OPEN_ON = 0.58
        self.OPEN_OFF = 0.50
        self.FIST_ON = 0.72
        self.FIST_OFF = 0.80
        self.PINCH_ENTER = 0.20
        self.PINCH_EXIT = 0.28

        self.frames_required = 7
        self.cooldown_s = 0.5
        self.level_hist = deque(maxlen=5)

    def update(self, features: HandFeatures, now=None):
        if now is None: 
            now = time.time()
        cooling = now < self._cooldown_until

        # openness stability counters
        if features.openness > self.OPEN_ON:
            self._open_stable += 1
            self._fist_stable = 0
        elif features.openness < self.FIST_ON:
            self._fist_stable += 1
            self._open_stable = 0
        else:
            # mid band
            self._open_stable = max(0, self._open_stable-1)
            self._fist_stable = max(0, self._fist_stable-1)

        intent = None

        # State transitions
        if self.mode == "IDLE":
            if not cooling and self._open_stable >= self.frames_required:
                intent = ("ON", None)
                self.target_level = max(self.target_level, 0.7)
                self._cooldown_until = now + self.cooldown_s
                self._open_stable = 0
                self.last_discrete = "ON"
            elif not cooling and self._fist_stable >= self.frames_required:
                intent = ("OFF", None)
                self.target_level = 0.0
                self._cooldown_until = now + self.cooldown_s
                self._fist_stable = 0
                self.last_discrete = "OFF"
            # Enter continuous level-set mode
            if features.pinch_ratio < self.PINCH_ENTER:
                self.mode = "SETLEVEL"
        else:  # SETLEVEL
            raw_level = max(0.0, min(1.0, (features.pinch_ratio - 0.02) / (self.PINCH_EXIT - 0.02)))
            raw_level = 1.0 - raw_level  # invert so small pinch = bright
            self.level_hist.append(raw_level)
            smooth_level = sum(self.level_hist)/len(self.level_hist)
            self.target_level = smooth_level
            intent = ("SET_LEVEL", self.target_level)

            # Exit when unpinched
            if features.pinch_ratio > self.PINCH_EXIT:
                self.mode = "IDLE"
                self.level_hist.clear()
                self._cooldown_until = now + 0.2  # brief pause

        # Smooth ramp to target
        dt = 1/30.0  # assume ~30 FPS
        max_step = self.ramp_per_sec * dt
        if self.filtered_level < self.target_level:
            self.filtered_level = min(self.filtered_level + max_step, self.target_level)
        else:
            self.filtered_level = max(self.filtered_level - max_step, self.target_level)

        return intent, self.filtered_level
