# gesture_light_control.py

import cv2
import mediapipe as mp
from gpiozero import PWMLED
from time import sleep

# === GPIO Setup ===
# Connect the dimmable light or LED to this GPIO pin
LED_PIN = 18
led = PWMLED(LED_PIN)

# === MediaPipe Hand Detection ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# === Video Capture ===
cap = cv2.VideoCapture(0)  # 0 = default camera

def get_brightness_from_landmarks(landmarks, frame_height):
    """
    Map finger height to brightness level (0.0 - 1.0)
    """
    index_finger_tip = landmarks[8]  # index finger tip landmark
    y_pos = index_finger_tip.y * frame_height  # normalized to pixel space

    # Map y_pos to brightness: top of frame = 1.0, bottom = 0.0
    brightness = 1.0 - (y_pos / frame_height)
    return max(0.0, min(brightness, 1.0))  # clamp between 0.0 and 1.0

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            continue

        # Flip for mirror view & convert to RGB
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)
        frame_height, frame_width, _ = frame.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get brightness from index finger position
                brightness = get_brightness_from_landmarks(hand_landmarks.landmark, frame_height)
                led.value = brightness  # update LED brightness
                cv2.putText(frame, f"Brightness: {brightness:.2f}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Gesture Light Control", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

finally:
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    led.close()
