# CameraWorkbench
Generalized usb camera software tailored for scientists collecting experiment data. Supports any number of cameras.
Includes detectors and failsafes for experiment hiccups.
Also includes camera throttling for preventing hitting the USB bandwidth cap. (Amscopes only.)

# Usage
```
python CameraWorkbench.py <--webcam|--amscope> <devices>
```
where ```devices``` is a list of integers denoting device index. Usually 0, 1, 2, etc...

# Dependencies
Only runs on OSX/Windows. Can be extended to Linux using the ToupCam SDK and editing 'Amscopy.py'. Requires: PyQt4, OpenCV.

# Planned features
- screenshot and email attachment features
- more cameras
