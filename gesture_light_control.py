# gesture_light_control.py
# Live hand tracking + gesture state machine + on-screen overlays.
# Works on Mac (DummyLED) and Raspberry Pi (gpiozero PWMLED).

import time
import cv2
import mediapipe as mp

from gesture_control import HandFeatures, GestureStateMachine

# -------- Output (Pi or Mac) --------
USE_PWM = True  # Set True on Pi. On Mac, it will auto-fallback to DummyLED.

class DummyLED:
    def __init__(self): self._v = 0.0
    @property
    def value(self): return self._v
    @value.setter
    def value(self, v):
        v = max(0.0, min(1.0, float(v)))
        if abs(v - self._v) >= 0.01:
            print(f"[LED] {int(v*100)}%")
        self._v = v
    def close(self): pass

try:
    if USE_PWM:
        from gpiozero import PWMLED
        LED_PIN = 18  # hardware PWM on Pi
        led = PWMLED(LED_PIN)
    else:
        led = DummyLED()
except Exception as e:
    print(f"[INFO] Falling back to DummyLED ({e})")
    led = DummyLED()

# -------- MediaPipe setup --------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
mp_draw = mp.solutions.drawing_utils

# -------- Video capture --------
# Keep default. If Continuity Camera picks your phone, that's fine for prototyping.
cap = cv2.VideoCapture(0)

# -------- State machine --------
sm = GestureStateMachine()

# -------- Helpers --------
def put_text(img, text, xy, scale=0.7, color=(0,255,0), thick=2):
    cv2.putText(img, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)

last_intent = None
last_intent_time = 0.0
frame_count = 0
t0 = time.time()

try:
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            print("Ignoring empty frame.")
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        openness_val = None
        pinch_val = None

        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            # ---- Features + state machine ----
            feats = HandFeatures(lm.landmark)
            openness_val = feats.openness
            pinch_val = feats.pinch_ratio

            intent, level = sm.update(feats)
            led.value = level

            # Cache the last intent to display for a short time
            if intent:
                last_intent = intent[0]
                last_intent_time = time.time()
        else:
            # No hand detected; keep current filtered level (no change)
            level = sm.filtered_level
            led.value = level

        # ---- Overlays ----
        h = frame.shape[0]
        y0 = 28
        dy = 28

        put_text(frame, "ESC to quit", (10, y0), 0.65, (200,200,200), 2)
        if openness_val is not None:
            put_text(frame, f"Openness:   {openness_val:.2f}", (10, y0+dy))
        if pinch_val is not None:
            put_text(frame, f"PinchRatio: {pinch_val:.2f}", (10, y0+2*dy))
        put_text(frame, f"Output: {int(sm.filtered_level*100):3d}%", (10, y0+3*dy))

        # Bottom-left: Mode + Intent (intent shown for ~1.0s after it triggers)
        put_text(frame, f"Mode: {sm.mode}", (10, h-60), 0.8, (0,200,255), 2)
        if last_intent and (time.time() - last_intent_time) < 1.0:
            put_text(frame, f"Intent: {last_intent}", (10, h-30), 0.8, (0,200,255), 2)

        # FPS (top-right)
        frame_count += 1
        if (time.time() - t0) > 0.5:
            fps = frame_count / (time.time() - t0)
            frame_count = 0
            t0 = time.time()
            put_text(frame, f"FPS: {fps:4.1f}", (frame.shape[1]-130, 28), 0.65, (200,200,200), 2)
        else:
            # Draw last FPS text again (lightweight: not recalculating each frame)
            pass

        cv2.imshow("Gesture Light Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

finally:
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    led.close()
