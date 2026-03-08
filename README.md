# Personal Projects

This repository contains my personal projects focused on **Embedded Systems, TinyML, Edge AI, Firmware development, and Autonomous Robotics**. The goal is to showcase hands-on engineering skills, real-time system design, and AI on resource-constrained devices.

---

## Projects

### RC Tank Autonomy (Flagship Project)
Autonomous RC tank platform with onboard perception and control.

**Features:**
- 360° obstacle sensing
- Semi-autonomous navigation
- Wall-following algorithm
- Turret targeting system with flywheel BB launcher

**Tech Stack:**
- Firmware: C/C++, Zephyr RTOS, FreeRTOS
- AI: TinyML, TensorFlow Lite Micro
- Hardware: STM32, IMU, Ultrasonic sensors, Motor drivers

**Notes:** Documentation, schematics, control algorithms, and demo videos coming soon.

---

### TinyML Projects
#### 1. Keyword Spotting
- Wake-word detection on MCU
- Audio preprocessing using MFCC
- CNN inference on embedded device

#### 2. Gesture Recognition (IMU)
- Recognizes gestures from accelerometer input
- Real-time inference using TinyML models

---

### Firmware & RTOS Projects
#### 1. Zephyr Sensor Node
- Multi-threaded sensor polling
- Message queues and BLE telemetry
- Ready for IoT integration

#### 2. FreeRTOS Motor Control
- Motor, sensor, and control tasks
- Demonstrates real-time task scheduling and concurrency

---

### Edge AI Projects
#### 1. Edge AI Camera
- Object detection on MCU
- TinyML model integration
- Optimized for low-latency inference

---

## Getting Started

Each project has its own folder with:
- Source code (`src` / `firmware`)
- Documentation (`README.md`)
- Optional demos or simulations (`demo/`)

Clone this repository and navigate to the project of interest:

```bash
git clone https://github.com/luca-guebeli/Personal-Projects.git
cd Personal-Projects/<project-name>
