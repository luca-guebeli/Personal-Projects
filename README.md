# Personal Projects

This repository contains my personal projects focused on **Embedded Systems, TinyML, Edge AI, Agentic AI, Firmware Development, and Autonomous Robotics**. The goal is to showcase hands-on engineering skills, real-time system design, AI on resource-constrained devices, and agent-based software systems.

---

## Projects

### RC Tank Autonomy (Flagship Project)
Autonomous RC tank platform with onboard perception and control.

**Features:**
- 360-degree obstacle sensing
- Semi-autonomous navigation
- Wall-following algorithm
- Turret targeting system with flywheel BB launcher

**Tech Stack:**
- Firmware: C/C++, FreeRTOS
- Hardware: STM32, IMU, IR sensors, motor drivers

**Hardware Components:**

#### 1. Core Logic & Communication
- **STM32G474RET6** - Main microcontroller (64-pin LQFP)
- **ESP32-C3-WROOM-02** - Wi-Fi/Bluetooth bridge for remote control

#### 2. Shooting Subsystem
- **Mabuchi FA-130RA Motor** - Flywheel motor (2-meter range)
- **MG90S Micro Servo** - Reloading pusher

#### 3. Turret & Drive Actuators
- **28BYJ-48 Stepper Motor** - 360-degree turret rotation
- **MG90S Micro Servo (Secondary)** - Barrel elevation control
- **N20 Gear Motors x2** - Left/right drive tracks

#### 4. Sensing & Power
- **10x VL53L0X ToF Modules** - Obstacle detection and mapping
- **DRV5032 Hall Effect Sensor** - Turret homing/alignment
- **MPU-6050 IMU** - Control

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
#### 1. STM32N6 Multimodal Edge AI
- Vision and audio experiments on an STM32N6 board
- Camera and MEMS microphone bring-up
- NPU-accelerated inference for real-time edge AI demos
- Center-object outline demo using camera-based segmentation
- Project folder: [STM32N6_Multimodal_Edge_AI](STM32N6_Multimodal_Edge_AI/)

#### 2. Edge AI Camera
- Object detection on MCU
- TinyML model integration
- Optimized for low-latency inference

---

### Agentic AI Projects
#### 1. Agent Learning Lab
- Experiments for learning how agents reason, plan, and use tools
- Small prototypes for task automation and workflow assistants
- Notes on agent architectures, memory, evaluation, and safety

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
```
