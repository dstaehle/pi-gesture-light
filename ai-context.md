# 🖐️ Hand Gesture Camera Light Switch — Project Summary

## Goal
Create a gesture-controlled light dimmer using a Raspberry Pi, a camera module, and AI-based hand tracking to recognize gestures and output a dimming signal (0–10V) to a lighting driver.

## Hardware
- Raspberry Pi 5 (with camera module)
- 5V→12V power supply (for lighting circuit)
- Camera module (PiCam or USB)
- Output options:
  - PWM to 0–10V converter *(or)*
  - MCP4725 DAC module

## Software Stack
- Python
- OpenCV (image processing)
- MediaPipe (hand detection and gesture tracking)
- RPi.GPIO or `gpiozero` (signal output)

## Current Status
- ✅ MediaPipe-based gesture tracking is functional
- ✅ Camera feed active and detecting hand landmarks
- 🔧 Working on mapping specific gestures to output values
- 🔧 Evaluating best method to convert digital signal to 0–10V analog dimming control
- 🔜 Next step: Classify gestures into "on", "off", "dim level" actions and output signal accordingly

## Open Questions
- Which is simpler and more reliable: PWM-to-0–10V vs. MCP4725 DAC?
- Should gesture recognition use landmark angles or ML-based classification?
- What’s the best way to debounce gesture recognition to avoid flicker?
