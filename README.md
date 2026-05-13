# 🖐️ Hand Gesture Volume Control

Control your computer's system volume using hand gestures — no keyboard, no mouse, just your hand in front of a webcam!

Built with **Python**, **OpenCV**, and **MediaPipe**.



## 🚀 Features

- 🎯 Real-time hand tracking with MediaPipe
- 🔊 Smooth volume control via thumb–index finger distance
- 📊 Live volume bar with color feedback (red → yellow → green)
- 🖥️ FPS counter and distance display
- 💡 Works on Windows (native audio API) and other platforms (PyAutoGUI fallback)
- 🔄 Mirrored webcam view for natural interaction

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| `opencv-python` | Webcam capture & frame rendering |
| `mediapipe` | Hand landmark detection |
| `numpy` | Numerical interpolation |
| `pycaw` | Windows native volume control |
| `pyautogui` | Fallback volume control |

---

## 📦 Installation

### Step 1 — Download and Install PyCharm Community Edition

1. Go to the official jetbrains website: [https://www.jetbrains.com/pycharm/download/](https://www.jetbrains.com/pycharm/download/)
2. Scroll down to PyCharm Community Edition (it is free) and click **Download**.
3. Run the `.exe` installer. 
4. Important: during installation, you can check the boxes for "Create Desktop Shortcut" and "Add 'bin' folder to the PATH".
5. Finish the setup wizard and launch PyCharm.

---

### Step 2 — Open the Project in PyCharm

1. Open PyCharm and click **Open**.
2. Navigate to your project folder: `c:\Users\ARYA MGC\open cv` and click **OK**.
3. PyCharm will discover `hand_volume_control.py`. Let it load.

---

### Step 3 — Install Required Libraries via PyCharm

To run this code, you must install `opencv-python`, `mediapipe`, `pyautogui`, and `pycaw`.

**Using the PyCharm Terminal:**
1. At the bottom of PyCharm, click the **Terminal** tab.
2. In the terminal, simply paste and run this command:
   ```bash
   pip install opencv-python mediapipe pyautogui pycaw comtypes
   ```
3. Wait for the libraries to install.

**Alternative: Using PyCharm Python Packages Tool**
1. At the bottom of PyCharm, look for the **Python Packages** tab.
2. Search for the library name (e.g. `opencv-python`), select it, and click **Install Package** on the right side.
3. Repeat for `mediapipe`, `pyautogui`, `pycaw`, and `comtypes`.

---

### Step 5 — Run the Project

```bash
python hand_volume_control.py
```

---

## 🎮 How to Use

| Gesture | Action |
|---|---|
| 👌 Pinch (thumb + index close) | Decrease volume |
| 🤏 Spread (thumb + index apart) | Increase volume |
| Press `Q` or `ESC` | Quit the application |

### Distance → Volume Mapping

```
Distance (pixels)    Volume
─────────────────────────────
30 px   (pinched)  →   0%
~115 px (mid)      →  50%
200 px  (open)     → 100%
```

---

## 📁 Project Structure

```
hand-gesture-volume-control/
│
├── hand_volume_control.py   # Main application
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🔧 Configuration

You can tweak these constants inside `hand_volume_control.py`:

```python
MIN_DIST = 30       # Pixel distance mapped to 0% volume
MAX_DIST = 200      # Pixel distance mapped to 100% volume
smooth_factor = 0.2 # Volume smoothing (0.0–1.0, lower = smoother)
```

---

## 🖥️ Platform Notes

| Platform | Volume Control Method |
|---|---|
| Windows | `pycaw` (native Windows Audio API) |
| macOS | `pyautogui` keyboard simulation |
| Linux | `pyautogui` keyboard simulation |

> For macOS/Linux native volume control, consider using `osascript` (macOS) or `amixer` (Linux) via `subprocess`.

---

## 🐛 Troubleshooting

**Camera not found?**
```bash
# Try changing the camera index in the code:
cap = cv2.VideoCapture(1)   # Try 0, 1, or 2
```

**mediapipe install fails?**
```bash
pip install --upgrade pip
pip install mediapipe
```

**pycaw not working?**
```bash
pip install pycaw comtypes
# Make sure you're on Windows
```

**Low FPS?**
- Close other applications using the webcam
- Reduce frame resolution in the code (`CAP_PROP_FRAME_WIDTH/HEIGHT`)

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

- [MediaPipe](https://mediapipe.dev/) by Google for hand tracking
- [OpenCV](https://opencv.org/) for computer vision
- [pycaw](https://github.com/AndreMiras/pycaw) for Windows audio control

---

## ⭐ Show Your Support

If you found this project helpful, give it a ⭐ on GitHub!
