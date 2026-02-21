import cv2
import mediapipe as mp
import subprocess
import numpy as np
from collections import deque


def set_volume(vol):
    vol = max(0, min(100, vol))
    subprocess.call(
        ["osascript", "-e", f"set volume output volume {vol}"]
    )

webcam = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
drawing_utils = mp.solutions.drawing_utils


volume_buffer = deque(maxlen=5)

MIN_DIST = 20
MAX_DIST = 200

while True:
    ret, img = webcam.read()
    img = cv2.flip(img, 1)
    frame_height, frame_width, _ = img.shape

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_img)

    x1 = y1 = x2 = y2 = 0
    volume = 0

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            drawing_utils.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

            landmarks = hand.landmark

            for id, lm in enumerate(landmarks):
                x = int(lm.x * frame_width)
                y = int(lm.y * frame_height)qq

                if id == 8:  # Index finger
                    x1, y1 = x, y
                    cv2.circle(img, (x, y), 8, (0, 255, 255), -1)

                if id == 4:  # Thumb
                    x2, y2 = x, y
                    cv2.circle(img, (x, y), 8, (0, 0, 255), -1)

        dist = int(np.hypot(x2 - x1, y2 - y1))

        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        volume = np.interp(dist, [MIN_DIST, MAX_DIST], [0, 100])
        volume = int(volume)

        volume_buffer.append(volume)
        smooth_volume = int(np.mean(volume_buffer))

        set_volume(smooth_volume)


        bar_x = 50
        bar_y = 150
        bar_height = 300
        bar_width = 35

        # Map volume to bar height
        bar_fill = np.interp(smooth_volume, [0, 100], [bar_height, 0])

        cv2.rectangle(img, (bar_x, bar_y),
                      (bar_x + bar_width, bar_y + bar_height),
                      (255, 255, 255), 3)

        cv2.rectangle(img,
                      (bar_x, int(bar_y + bar_fill)),
                      (bar_x + bar_width, bar_y + bar_height),
                      (0, 255, 0), -1)

        cv2.putText(img, f'{smooth_volume} %',
                    (40, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 3)

    cv2.putText(img, "Hand Gesture Volume Control",
                (150, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 0), 2)

    cv2.imshow("Hand Volume Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()
