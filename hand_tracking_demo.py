import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)  # Use Mac webcam

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read from camera")
        break
    else:
        print("📸 Frame captured")


    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Draw landmarks
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    # Show the video feed
    cv2.imshow("Hand Tracking", frame)

    # Quit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Failed to access camera")
else:
    print("✅ Camera opened successfully")

