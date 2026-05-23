# Center-Object Outline Demo

## Goal

Build a real-time camera demo that outlines the dominant object near the center of the B-CAMS-IMX image.

The first version should be simple and observable. The final version can use an STM32N6-optimized segmentation model, but the project should start with a classical computer-vision baseline so the camera path, frame format, and overlay code are proven before the model is involved.

## Why Segmentation

Object detection is good for drawing bounding boxes. This demo needs an object outline, so the system needs either:

- a segmentation mask from a model
- a contour extracted from image processing
- a hybrid of both

For the first serious model, use binary segmentation: foreground centered object vs background.

## MVP Pipeline

1. Capture a frame from B-CAMS-IMX.
2. Resize or crop the frame around the center.
3. Convert to the model or baseline input format.
4. Produce a foreground mask or contour.
5. Keep the connected region nearest the image center.
6. Smooth the mask enough to remove noise.
7. Trace the contour.
8. Draw the outline back onto the displayed or streamed frame.
9. Log frame time, inference time, and post-processing time.

## Baseline Before The Model

Start with a no-model baseline:

- Center crop
- Empty-background capture
- Background subtraction in Lab color space
- Optional center-color segmentation
- Connected-component or contour selection
- Keep the contour closest to the center point

This will not be robust in every lighting condition, but it will reveal whether the camera, memory buffers, and overlay path are working. The background-subtraction path is the most useful first baseline because it can separate bright and dark objects as long as the camera and background remain stable.

The first PC-side baseline lives in:

```text
tools/center_object_outline_pc/
```

Run it against the STM32 USB camera stream before moving the algorithm onto the board.

## Model Direction

Use a two-stage model path:

- PC model: train a stronger residual U-Net-style binary segmentation model to prove the dataset and labels.
- STM32N6 model: compress the idea into a smaller INT8 model for on-device inference.

The final embedded model should still be compact:

- Input: 160x160 or 224x224 RGB image
- Output: low-resolution binary foreground mask
- Architecture candidates: small U-Net, MobileNet-style encoder with light decoder, or another compact segmentation network
- Quantization: INT8
- Target runtime: STM32N6 with ST Edge AI tooling and the Neural-ART accelerator where supported

Avoid starting with large general models such as foundation segmentation models. They are useful references, but they are not a practical first target for an MCU deployment.

## Dataset Plan

Collect a small custom dataset with the real camera:

- Centered objects on the desk
- Objects slightly off-center
- Empty background
- Different lighting
- Different distances
- Similar object/background colors
- Motion blur examples

Label each frame with a binary mask:

- Foreground: the object intended to be outlined
- Background: everything else

Start narrow. A dataset of familiar desk objects and electronics parts is more useful than trying to recognize every possible object.

## Post-Processing

After the baseline or model produces a mask:

- Threshold the mask
- Remove small regions
- Keep the component with the strongest overlap with the center region
- Smooth jagged edges if needed
- Trace the contour
- Draw a bright outline over the original frame

The B-CAMS-IMX ToF sensor may later help choose the foreground object if the visual mask is ambiguous.

## Success Criteria

- Outlines the centered object in a repeatable desk setup
- Fails gracefully when no clear centered object exists
- Runs fast enough to feel interactive
- Logs enough timing information to know the bottleneck
- Produces screenshots or short clips for the README

## Open Questions

- Which STM32N6 board model is being used?
- Where will the outline be shown: LCD, USB stream, serial debug image dump, or saved frames?
- Which object family should the first dataset target?
- Should audio trigger the outline demo, or should audio come after the vision path is stable?
