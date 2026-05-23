# STM32N6 Multimodal Edge AI

This project is a hands-on lab for building real-time edge AI applications on an STM32N6 board using a camera module and MEMS microphones.

The goal is to move from hardware bring-up to working demos that combine vision, audio, and on-device inference.

## Hardware

- STM32N6 development board
- NUCLEO-N657X0-Q board
- B-CAMS-IMX camera module bundle
- X-NUCLEO-CCA02M2 digital MEMS microphone expansion board
- USB debug/programming cable
- Optional: microSD card, display, external sensors, enclosure

Exact part numbers and board revisions are tracked in [docs/hardware.md](docs/hardware.md).

## Project Tracks

### 1. Board Bring-Up
- Install STM32CubeIDE / STM32CubeMX / STM32CubeProgrammer
- Confirm ST-LINK connection
- Flash a minimal firmware example
- Set up serial logging or semihosting for debug output

### 2. Camera Bring-Up
- Confirm the camera interface and driver stack
- Capture a test frame
- Validate resolution, pixel format, frame rate, and memory placement
- Save, stream, or display a known-good frame

Detailed notes: [docs/camera-bringup.md](docs/camera-bringup.md)

### 3. Audio Bring-Up
- Confirm MEMS microphone interface and clocking
- Capture raw audio buffers
- Validate sample rate, bit depth, channel count, and signal level
- Add simple diagnostics such as RMS level and FFT peak checks

### 4. Vision Inference
- Start with a small image classification or object detection model
- Convert and optimize the model for STM32N6 deployment
- Measure inference latency, memory use, and frame throughput

### 5. Center-Object Outline Demo
- Detect or segment the dominant object nearest the center of the camera frame
- Convert the result into a clean outline overlay
- Use low-resolution model input while preserving enough visual detail for the outline
- Track latency, frame rate, and failure cases

Detailed notes: [docs/center-object-outline.md](docs/center-object-outline.md)

### 6. Audio Inference
- Start with keyword spotting or sound event classification
- Build the preprocessing path, such as framing and MFCC extraction
- Measure end-to-end latency from microphone input to prediction

### 7. Multimodal Demo
- Combine camera and microphone signals in one real-time loop
- Use audio to wake or trigger vision processing
- Use vision results to change system behavior
- Log model confidence, timing, and failure cases

## First Milestones

- [ ] Identify the exact STM32N6 board model and revision
- [x] Identify the STM32N6 board family
- [x] Identify the exact camera module and interface
- [x] Identify the exact MEMS microphone hardware
- [ ] Flash a known-good STM32CubeN6 example
- [x] Capture one camera frame
- [ ] Capture one second of microphone audio
- [x] Run the first center-object outline baseline
- [x] Label first segmentation dataset
- [x] Train first PC segmentation baseline
- [ ] Run the first AI model on target
- [ ] Document the first complete demo

## Repository Layout

```text
STM32N6_Multimodal_Edge_AI/
|-- README.md
|-- data/
|   `-- README.md
|-- docs/
|   |-- bringup-plan.md
|   |-- camera-bringup.md
|   |-- center-object-outline.md
|   `-- hardware.md
|-- firmware/
|   `-- README.md
|-- models/
|   `-- README.md
|-- training/
|   `-- center_object_segmentation/
`-- tools/
    `-- center_object_outline_pc/
```

## References

- [STM32N6 series - STMicroelectronics](https://www.st.com/en/microcontrollers-microprocessors/stm32n6-series.html)
- [STM32N6 AI ecosystem - STMicroelectronics](https://www.st.com/en/development-tools/stm32n6-ai.html)
- [STM32N6570-DK data brief - STMicroelectronics](https://www.st.com/resource/en/data_brief/stm32n6570-dk.pdf)
- [B-CAMS-IMX data brief - STMicroelectronics](https://www.st.com/resource/en/data_brief/b-cams-imx.pdf)
- [B-CAMS-IMX user manual - STMicroelectronics](https://www.st.com/resource/en/user_manual/um3354-camera-module-for-stm32-boards-stmicroelectronics.pdf)
- [X-NUCLEO-CCA02M2 product page - STMicroelectronics](https://www.st.com/en/evaluation-tools/x-nucleo-cca02m2.html)
