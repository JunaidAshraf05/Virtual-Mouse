import cv2
import mediapipe as mp
import pyautogui
import time
import math

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

print(cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

click_cooldown = 0.15  # seconds, reduced for more responsiveness
last_click_time = 0

# Smoothing variables
prev_x, prev_y = 0, 0
smoothing = 0.2  

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks
    if hands:
        for hand in hands:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark
            index_x = index_y = thumb_x = thumb_y = None
            index_px = index_py = thumb_px = thumb_py = None

            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                if id == 8:
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255), thickness=-1)
                    # Calculate target screen coordinates
                    target_x = screen_width / frame_width * x
                    target_y = screen_height / frame_height * y
                    index_px, index_py = x, y
                    # Smooth movement
                    smooth_x = prev_x + (target_x - prev_x) * smoothing
                    smooth_y = prev_y + (target_y - prev_y) * smoothing
                    pyautogui.moveTo(smooth_x, smooth_y)
                    prev_x, prev_y = smooth_x, smooth_y
                    index_x, index_y = smooth_x, smooth_y
                if id == 4:
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255), thickness=-1)
                    thumb_x = screen_width / frame_width * x
                    thumb_y = screen_height / frame_height * y
                    thumb_px, thumb_py = x, y

            # More responsive click detection using Euclidean distance
            if (
                index_x is not None and index_y is not None and
                thumb_x is not None and thumb_y is not None
            ):
                distance = math.hypot(index_px - thumb_px, index_py - thumb_py)
                if distance < 35:
                    current_time = time.time()
                    if current_time - last_click_time > click_cooldown:
                        pyautogui.click()
                        last_click_time = current_time
                        # Optional: Visual feedback for click
                        cv2.circle(frame, (index_px, index_py), 20, (0, 0, 255), 3)

    cv2.imshow('Virtual mouse', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()