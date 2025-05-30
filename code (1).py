"""
Driver Drowsiness and Sleep Detection System with Alarm Sound.

Requirements:
- Python packages: opencv-python, dlib, scipy, pyttsx3, numpy
- Download 'shape_predictor_68_face_landmarks.dat' from:
  http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
  Unzip and place in the same folder.

- If on Windows, no additional setup for beep alarm.
- For other OS, consider additional setup or replace beep function.

Quit program: Press 'q'
"""

import cv2
import dlib
import pyttsx3
from scipy.spatial import distance
import numpy as np
import time
import threading
import platform

# Check OS for beep sound implementation
ON_WINDOWS = platform.system() == "Windows"
if ON_WINDOWS:
    import winsound
else:
    # For non-Windows, define beep function (minimal)
    import os

    def beep(frequency=1000, duration=200):
        # Simple beep for Linux/macOS using 'beep' command if installed
        os.system('play -nq -t alsa synth {} sine {}'.format(duration/1000, frequency))


# Constants
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 20  # ~0.66 seconds at 30fps for drowsiness
SLEEP_CONSEC_FRAMES = 90  # ~3 seconds at 30fps for sleep

# Initialize counters and alarm flags
COUNTER = 0
ALARM_ON = False
ALARM_THREAD = None
STOP_ALARM_EVENT = threading.Event()

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Dlib face detector and landmark predictor path
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

LEFT_EYE_POINTS = list(range(42, 48))
RIGHT_EYE_POINTS = list(range(36, 42))


def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords


def play_alarm_sound():
    """
    Play continuous alarm sound until STOP_ALARM_EVENT is set.
    """
    if ON_WINDOWS:
        # On Windows use winsound.Beep in a loop
        while not STOP_ALARM_EVENT.is_set():
            winsound.Beep(2000, 500)  # frequency in Hz, duration in ms
            time.sleep(0.1)
    else:
        # For other OSes, you can replace this with your own beep or sound play method
        while not STOP_ALARM_EVENT.is_set():
            beep(2000, 500)  # simple beep
            time.sleep(0.1)


def sound_alert(text):
    """
    Speak the alert message once.
    """
    engine.say(text)
    engine.runAndWait()


def start_alarm(text):
    global ALARM_ON, ALARM_THREAD, STOP_ALARM_EVENT
    if not ALARM_ON:
        ALARM_ON = True
        STOP_ALARM_EVENT.clear()

        # Start beep thread
        ALARM_THREAD = threading.Thread(target=play_alarm_sound)
        ALARM_THREAD.daemon = True
        ALARM_THREAD.start()

        # Speak alert once
        sound_alert(text)


def stop_alarm():
    global ALARM_ON, STOP_ALARM_EVENT, ALARM_THREAD
    if ALARM_ON:
        STOP_ALARM_EVENT.set()
        if ALARM_THREAD is not None:
            ALARM_THREAD.join()
        ALARM_ON = False


def main():
    global COUNTER

    print("[INFO] Starting video stream...")
    cap = cv2.VideoCapture(0)
    time.sleep(1.0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = shape_to_np(shape)

            leftEye = shape[LEFT_EYE_POINTS]
            rightEye = shape[RIGHT_EYE_POINTS]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            # Draw eye contours
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if EYE_AR_CONSEC_FRAMES <= COUNTER < SLEEP_CONSEC_FRAMES:
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    start_alarm("Drowsiness detected. Please stay awake!")
                elif COUNTER >= SLEEP_CONSEC_FRAMES:
                    cv2.putText(frame, "SLEEP ALERT! WAKE UP!", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                    start_alarm("Sleep detected. Wake up immediately!")
            else:
                COUNTER = 0
                stop_alarm()

            cv2.putText(frame, f"EAR: {ear:.2f}", (500, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        cv2.imshow("Drowsiness and Sleep Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    stop_alarm()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

