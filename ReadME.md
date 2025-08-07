# Pi-Gesture-Light

A gesture-controlled dimmer system built using OpenCV, MediaPipe, and Raspberry Pi GPIO. This project demonstrates real-time input processing and hardware-software integration for interactive physical systems.

## 🎯 Project Overview

**Pi-Gesture-Light** translates hand gestures into dimming signals to control a light source. By using a webcam and hand tracking, the system adjusts brightness through PWM output on the Raspberry Pi.

- 👋 Hand-based UI (no physical controls)
- 📷 Computer vision via OpenCV + MediaPipe
- ⚡ Real-time GPIO control via Raspberry Pi
- 🌐 Designed for embedded edge deployment

---

## 🧰 Tech Stack

- **Language:** Python 3
- **Computer Vision:** OpenCV, MediaPipe
- **Hardware Interface:** RPi.GPIO or `gpiozero`
- **Platform:** Raspberry Pi (tested on Pi 4)

---

## 🖼 How It Works

1. Camera detects a user's hand in frame
2. MediaPipe identifies landmarks (e.g., finger tips)
3. Brightness level is calculated from distance/gesture
4. PWM signal is adjusted in real time via GPIO pin
5. Light source dims or brightens accordingly

---

## 🚀 Getting Started

### Prerequisites
- Raspberry Pi with GPIO-enabled OS
- Webcam or Pi Camera Module
- Python 3.7+
- Installed dependencies:  
  ```bash
  pip install opencv-python mediapipe gpiozero
