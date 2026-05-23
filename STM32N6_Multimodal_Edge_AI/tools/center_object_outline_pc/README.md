# Center-Object Outline PC Prototype

This tool uses the STM32N6 camera stream as a normal USB webcam and draws an outline around the most likely object near the center of the frame.

It is intentionally a PC prototype. The goal is to tune the idea quickly before implementing a smaller version on the STM32N6.

## Setup

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Try camera index `1` first if your PC has a built-in webcam:

```powershell
python outline_webcam.py --camera-index 1
```

The default method is `background`:

1. Point the camera at the empty background.
2. Press `b` to capture that background.
3. Put the object in the center.
4. Watch the green outline.

If that opens the wrong camera, try another index:

```powershell
python outline_webcam.py --camera-index 0
python outline_webcam.py --camera-index 2
```

## Controls

- `q`: quit
- `s`: save the current raw frame and annotated preview
- `m`: switch between `background`, `color`, `grabcut`, and `edges`
- `b`: capture the current frame as the empty background for `background` mode
- `r`: reset the captured background and timing state

## Useful Arguments

```powershell
python outline_webcam.py --camera-index 1 --width 800 --height 480 --fps 30
python outline_webcam.py --camera-index 1 --width 640 --height 480 --fps 30 --process-scale 0.5
python outline_webcam.py --camera-index 1 --width 480 --height 480 --fps 30 --process-scale 0.5
python outline_webcam.py --camera-index 1 --method background --process-scale 0.35 --process-every 2
python outline_webcam.py --camera-index 1 --method background --diff-threshold 22
python outline_webcam.py --camera-index 1 --method color --color-threshold 38
python outline_webcam.py --camera-index 1 --method edges
python outline_webcam.py --camera-index 1 --center-width 0.55 --center-height 0.70
python outline_webcam.py --camera-index 1 --save-dir ..\..\data\samples\camera
```

## Notes

The `background` method is best for the first bench test. It compares the current frame against an empty-scene snapshot, so it handles bright and dark objects better than simple edge detection when the camera and lighting stay still.

The `color` method samples the color at the center of the frame and keeps pixels with similar color in Lab color space. It can work well for solid-color objects, but it can fail when the background has a similar color.

The `grabcut` method assumes the object is inside a centered rectangle and estimates foreground/background. It is useful for proving the outline idea, but it will fail in cluttered scenes.

The `edges` method is faster and simpler. It works best when the centered object has strong contrast against the background.

## Improving Refresh Rate

The ST camera-capture firmware advertises 30 fps streams at several sizes. If the Python view is choppy, reduce host-side work first:

- use `background` or `color`, not `grabcut`
- use `--process-scale 0.5` or `--process-scale 0.35`
- use `--process-every 2` to update the outline every other frame
- request a smaller stream, such as `--width 640 --height 480` or `--width 480 --height 480`
- close Windows Camera, OBS, Teams, or any other app that may still hold the camera

Start with:

```powershell
python outline_webcam.py --camera-index 1 --width 640 --height 480 --fps 30 --method background --process-scale 0.35 --process-every 2
```

After collecting samples with `s`, label the raw frames:

```powershell
cd ..\..\training\center_object_segmentation
python label_masks.py --input-dir ..\..\data\samples\camera --output-root ..\..\data\segmentation --split train
```
