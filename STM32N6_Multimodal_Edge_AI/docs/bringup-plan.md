# Bring-Up Plan

This plan is ordered so each step proves one layer before depending on it.

## Phase 0: Identify The Hardware

- Record board model, board revision, and MCU marking
- Record camera module part number and connector type
- Record microphone part number or daughterboard name
- Photograph jumper settings and cable setup
- Link relevant ST user manuals and schematics

## Phase 1: Development Environment

- Install STM32CubeIDE
- Install STM32CubeProgrammer
- Install STM32CubeMX if project generation is needed
- Install STM32CubeN6 package
- Confirm board appears in the debugger/programmer
- Flash an official example without modifications

Exit criteria:
- Firmware flashes reliably
- Debugger can halt, reset, and single-step
- A basic log message is visible

## Phase 2: Camera Path

- Connect and verify the B-CAMS-IMX 22-pin FFC orientation with the board unpowered
- Start with ST's x-cube-n6-camera-capture prebuilt NUCLEO binary to prove the camera as a USB webcam
- If the prebuilt path works, move to source-level bring-up with STM32CubeIDE or STM32CubeN6 DCMIPP examples
- Verify clocks, pins, and memory configuration
- Capture a frame into a known buffer
- Confirm frame dimensions and pixel format
- Export or display a test frame

Exit criteria:
- One valid frame is visible through USB UVC or captured repeatedly in firmware
- Frame timing is measured
- Buffer ownership is understood

Detailed checklist: [camera-bringup.md](camera-bringup.md)

## Phase 3: Audio Path

- Connect and verify the X-NUCLEO-CCA02M2 board orientation and headers
- Start from the closest STM32CubeN6 audio or microphone example
- Verify microphone clocking and DMA
- Capture raw audio into a ring buffer
- Add signal-level diagnostics
- Save or stream a short sample for inspection

Exit criteria:
- One second of valid audio is captured
- Sample rate and channel count are documented
- Clipping and silence are easy to detect

## Phase 4: First Model

- Choose one tiny baseline model first
- Convert to the format required by ST Edge AI tooling
- Benchmark on host or developer cloud if useful
- Deploy to target
- Log inference latency and memory footprint

Exit criteria:
- A model runs on target
- Input preprocessing is documented
- Output classes and confidence values are logged

## Phase 5: Center-Object Outline Demo

- Start with a no-model baseline: center crop, edge detection, contour selection, and outline overlay
- Select the connected component or contour closest to the image center
- Move to a tiny binary segmentation model once camera capture and overlay are stable
- Feed a small resized frame or center crop to the model
- Post-process the mask into a clean outline
- Measure camera frame time, model time, post-processing time, and total loop time

Exit criteria:
- The system draws an outline around the dominant centered object
- The baseline and model outputs can be compared on the same scene
- Failure cases are documented with example frames

## Phase 6: Multimodal Demo

- Use audio as a wake or trigger signal
- Run vision only when needed
- Combine predictions in a simple state machine
- Measure total loop latency
- Record limitations and failure cases

Exit criteria:
- A repeatable demo runs from power-on
- Timing, memory, and model behavior are documented
- Demo steps are clear enough to reproduce
