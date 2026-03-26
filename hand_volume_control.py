"""
Hand Gesture Volume Control
============================
Control your system volume using hand gestures via webcam.
Compatible with mediapipe 0.10.30+ and Python 3.12/3.13/3.14
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import math
import time
import os
import urllib.request

# Try to import Windows volume control
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    WINDOWS_VOLUME = True
except ImportError:
    WINDOWS_VOLUME = False


# ─────────────────────────────────────────────
#  Download Model Helper
# ─────────────────────────────────────────────

def get_model():
    model_path = "hand_landmarker.task"
    if not os.path.exists(model_path):
        print("[INFO] Downloading hand landmarker model (~8MB), please wait...")
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, model_path)
        print("[INFO] Model downloaded successfully!")
    return model_path


# ─────────────────────────────────────────────
#  Hand Detector Class (New MediaPipe API)
# ─────────────────────────────────────────────

class HandDetector:
    def __init__(self, max_hands=1, detection_conf=0.7, tracking_conf=0.7):
        self.results = None
        self.tip_ids = [4, 8, 12, 16, 20]

        base_options = python.BaseOptions(model_asset_path=get_model())
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
            min_hand_presence_confidence=detection_conf
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        self.results = self.detector.detect(mp_image)

        if draw and self.results.hand_landmarks:
            h, w = img.shape[:2]
            for hand_landmarks in self.results.hand_landmarks:
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 4, (0, 255, 0), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0, draw=False):
        lm_list = []
        if not self.results or not self.results.hand_landmarks:
            return lm_list
        if hand_no >= len(self.results.hand_landmarks):
            return lm_list

        h, w = img.shape[:2]
        for idx, lm in enumerate(self.results.hand_landmarks[hand_no]):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append([idx, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lm_list

    def fingers_up(self, lm_list):
        fingers = []
        if len(lm_list) < 21:
            return fingers
        fingers.append(1 if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0]-1][1] else 0)
        for i in range(1, 5):
            fingers.append(1 if lm_list[self.tip_ids[i]][2] < lm_list[self.tip_ids[i]-2][2] else 0)
        return fingers

    def find_distance(self, p1, p2, img, lm_list, draw=True):
        if len(lm_list) < max(p1, p2) + 1:
            return 0, img, []
        x1, y1 = lm_list[p1][1], lm_list[p1][2]
        x2, y2 = lm_list[p2][1], lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


# ─────────────────────────────────────────────
#  Volume Controller
# ─────────────────────────────────────────────

class VolumeController:
    def __init__(self):
        self.volume_interface = None
        self.min_vol = 0
        self.max_vol = 100
        self.current_vol = 50 # Default tracker if pycaw fails

        if WINDOWS_VOLUME:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
                self.min_vol, self.max_vol, _ = self.volume_interface.GetVolumeRange()
                print("[INFO] Windows Audio API ready.")
            except Exception as e:
                print(f"[WARN] Audio API failed: {e}")
                print("[INFO] Falling back to PyAutoGUI keystrokes mapping.")
        else:
            print("[INFO] Install pycaw for real volume control: pip install pycaw comtypes")

    def set_volume(self, percent):
        percent = max(0, min(100, percent))
        if self.volume_interface:
            vol = np.interp(percent, [0, 100], [self.min_vol, self.max_vol])
            self.volume_interface.SetMasterVolumeLevel(vol, None)
        else:
            # Fallback to PyAutoGUI
            # Each keystroke changes volume by ~2%. We calculate the difference.
            diff = percent - self.current_vol
            if abs(diff) > 2:
                steps = int(abs(diff) / 2)
                if diff > 0:
                    import pyautogui
                    pyautogui.press('volumeup', presses=steps)
                else:
                    import pyautogui
                    pyautogui.press('volumedown', presses=steps)
                self.current_vol += steps * 2 * (1 if diff > 0 else -1)
        return percent


# ─────────────────────────────────────────────
#  UI Helpers
# ─────────────────────────────────────────────

def draw_volume_bar(img, vol_percent):
    bar_x, bar_y, bar_w, bar_h = 50, 150, 35, 200
    cv2.rectangle(img, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (50, 50, 50), cv2.FILLED)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (150, 150, 150), 2)
    fill_h = int(np.interp(vol_percent, [0, 100], [0, bar_h]))
    fill_y = bar_y + bar_h - fill_h
    color = (0, 100, 255) if vol_percent < 30 else (0, 200, 255) if vol_percent < 70 else (0, 230, 100)
    cv2.rectangle(img, (bar_x, fill_y), (bar_x+bar_w, bar_y+bar_h), color, cv2.FILLED)
    cv2.putText(img, f'{int(vol_percent)}%', (bar_x-5, bar_y+bar_h+30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(img, 'VOL', (bar_x+2, bar_y-15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)


def draw_overlay(img, fps, vol_percent):
    h, w = img.shape[:2]
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, 55), (20, 20, 20), cv2.FILLED)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    cv2.putText(img, 'Hand Gesture Volume Control',
                (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 255), 2)
    fps_color = (0, 255, 0) if fps > 20 else (0, 165, 255)
    cv2.putText(img, f'FPS: {int(fps)}', (w-120, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
    cv2.putText(img, 'Pinch thumb & index finger to adjust volume',
                (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Hand Gesture Volume Control")
    print("  Press Q or ESC to quit")
    print("=" * 50)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    detector = HandDetector(max_hands=1, detection_conf=0.75, tracking_conf=0.75)
    vol_ctrl = VolumeController()

    MIN_DIST, MAX_DIST = 30, 200
    smoothed_vol = 50.0
    smooth_factor = 0.2
    prev_time = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img, draw=True)
        lm_list = detector.find_position(img, draw=False)

        if lm_list:
            distance, img, line_info = detector.find_distance(4, 8, img, lm_list, draw=True)
            target_vol = np.interp(distance, [MIN_DIST, MAX_DIST], [0, 100])
            smoothed_vol += smooth_factor * (target_vol - smoothed_vol)
            vol_ctrl.set_volume(smoothed_vol)
            if line_info and distance < 50:
                cv2.circle(img, (line_info[4], line_info[5]), 15, (0, 255, 0), cv2.FILLED)

        draw_volume_bar(img, smoothed_vol)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        draw_overlay(img, fps, smoothed_vol)
        cv2.imshow('Hand Gesture Volume Control', img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()