# Logic PCB Schematic Group Plan

This document divides the logic PCB schematic into groups. Work them in order and review each group before moving on.

## 1. Group Order

| Group | Sheet | Purpose | Status |
|---:|---|---|---|
| 1 | `01_USB_C_Input_Protection` | USB-C 5 V input, USB D+/D-, ESD, eFuse, rear power enable, protected `SYS_5V`. | Start here |
| 2 | `02_3V3_Buck_Regulator` | Generate `SYS_3V3` from protected `SYS_5V`. | Next |
| 3 | `03_ESP32S3_Core` | ESP32-S3 module, EN/BOOT, USB, decoupling, antenna/mechanical notes. | Pending |
| 4 | `04_Display_Touch_Backlight` | 40-pin TFT FFC, 6-pin touch FFC, backlight current driver. | Pending |
| 5 | `05_Scanner_Interface` | Waveshare scanner connector, 5 V load switch, UART level shifting. | Pending |
| 6 | `06_HMI_Connector` | JST-GH 14-pin connector to front-panel PCB. | Pending |
| 7 | `07_Buzzer_Status` | Buzzer driver and optional status/test LED. | Pending |
| 8 | `08_Debug_Test_Points` | Boot/reset/test pads, bring-up probing, optional Tag-Connect. | Pending |
| 9 | `09_System_Checks` | Net classes, ERC cleanup, notes, power-tree review. | Pending |

## 2. Group 1 - USB-C Input And Protected 5 V Rail

### 2.1 Goal

Create the raw 5 V input path and the protected system 5 V rail:

```text
USB-C VBUS
  -> ESD / TVS / input capacitance
  -> TPS259531 eFuse
  -> SYS_5V
```

Also route USB D+/D- to the ESP32-S3 native USB pins through ESD protection.

### 2.2 Components

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `J1` | USB-C receptacle | `USB4105-GF-A` | USB 2.0 Type-C receptacle. |
| `U1` | USB ESD array | `USBLC6-2SC6` | Protect D+/D- and VBUS class USB lines. Place close to `J1`. |
| `R1`, `R2` | CC pulldowns | 5.1 kΩ, 1% | `CC1` to GND, `CC2` to GND. |
| `U2` | eFuse | `TPS259531DSGR` | Protected 5 V system path. |
| `J_PWR` or `SW_PWR` | Main power switch interface | NKK `UB216KKG015C`; `EG1218` only as hidden service fallback | Drives eFuse enable/UVLO logic. |
| `C_IN1` | eFuse input decoupling | 100 nF, X7R, 50 V, 0603, 10% | Place close to TPS2595 IN/GND pins. |
| `C_IN2` | optional USB/eFuse input bulk | 1 µF, X7R, 25 V or 50 V, 0603/0805, 10% | Place near eFuse input if USB cable/input path is noisy. |
| `C_OUT1` | eFuse output cap | 1 µF, X7R, 25 V, 0603 or 0805, 10% | Place close to TPS2595 OUT/GND. |
| `C_SYS5_BULK` | protected 5 V rail bulk | 10-22 µF, X5R/X7R, 16 V or 25 V, 0805/1206, 10-20% | Place on `SYS_5V` after eFuse. |
| `R_ILM` | Current limit resistor | Value TBD | Sets TPS2595 current limit. Start target around 1.5-2.0 A. |
| `C_DVDT` | Slew-rate capacitor | 3.3 nF, C0G/NP0, 50 V, 0603, 5-10% | Controls output ramp/inrush; use C0G because this is timing-related. |
| `R_FLT` | Fault pull-up | 10 kΩ class | Pull `EFUSE_FLT` to 3.3 V or use test pad only; confirm open-drain behavior in datasheet. |
| `TVS1` | VBUS TVS | TBD | Optional/likely useful near USB connector. Choose 5 V USB/power TVS. |

### 2.3 Nets To Create

| Net | Meaning |
|---|---|
| `USB_VBUS` | Raw 5 V from USB-C connector. |
| `USB_D_N` | USB D- after connector/ESD routing. Goes to ESP32 GPIO19. |
| `USB_D_P` | USB D+ after connector/ESD routing. Goes to ESP32 GPIO20. |
| `CC1` | USB-C CC1 with 5.1 kΩ pulldown. |
| `CC2` | USB-C CC2 with 5.1 kΩ pulldown. |
| `SYS_EN` | Power enable from rear switch/eFuse enable network. |
| `EFUSE_FLT` | Fault output/test net. |
| `SYS_5V` | Protected 5 V rail after eFuse. |
| `GND` | System ground. |

### 2.4 USB-C Wiring

Wire the USB-C receptacle as a simple 5 V sink:

- All VBUS pins to `USB_VBUS`.
- All GND pins to `GND`.
- `CC1` to GND through 5.1 kΩ.
- `CC2` to GND through 5.1 kΩ.
- D+ pins tied together as `USB_D_P`.
- D- pins tied together as `USB_D_N`.
- Shield pins: connect to chassis/ground strategy. First pass can use shield to GND through a placeholder network, such as 0 Ω / RC / DNP options.

No USB-PD controller is used in v1.

Reason:

- The product only needs 5 V input.
- Expected current is comfortably in the normal USB-C 5 V appliance range.
- A USB-PD controller is only needed if the design must negotiate higher voltage/current, such as 9 V, 12 V, 15 V, or 20 V contracts, or needs more advanced Type-C role behavior.
- The v1 design remains a fixed 5 V USB-C sink using CC pulldown resistors.

### 2.5 USB ESD Wiring

Place `USBLC6-2SC6` close to the USB-C connector.

Connect:

- Pin 1 `I/O1_1` and pin 6 `I/O1_2` to `USB_D_P`.
- Pin 3 `I/O2_1` and pin 4 `I/O2_2` to `USB_D_N`.
- `VBUS` pin to `USB_VBUS`.
- `GND` pin to `GND`.

Layout note:

- Keep ESD path to ground short.
- Keep USB D+/D- as a differential pair from connector to ESP32.
- For USB 2.0 full-speed/native ESP32 programming this is not brutally hard, but still route cleanly.
- Route D+ and D- physically through the ESD pads if possible: connector -> ESD pins -> ESP32.

### 2.6 eFuse Wiring

Use `TPS259531DSGR` between `USB_VBUS` and `SYS_5V`.

Functional wiring:

- eFuse input pins to `USB_VBUS`.
- eFuse output pins to `SYS_5V`.
- eFuse ground/exposed pad to `GND`.
- Enable/UVLO pin controlled by `SYS_EN` rear-switch network.
- Current-limit/load-monitor pin configured by `R_ILM`.
- dVdt/slew pin configured by `C_DVDT`.
- Fault pin to `EFUSE_FLT` with pull-up or test pad.

Initial design targets:

- Current limit: around 1.5-2.0 A. This gives margin for scanner, display backlight, ESP32 Wi-Fi peaks, LEDs, and future bring-up without making faults too violent.
- Output ramp: moderate/soft enough to avoid scanner/backlight/display inrush surprises.

Good first-pass values:

- `R_ILM = 1.37 kΩ` for about 1.5 A current limit.
- `R_ILM = 1.02 kΩ` for about 2.0 A current limit.
- `C_DVDT = 3.3 nF` for a controlled but still quick 5 V output ramp.

Use 1.5 A as the first schematic target unless later current-budget testing says otherwise.

### 2.7 Main Power Switch

Preferred behavior:

```text
power switch OFF -> eFuse disabled -> SYS_5V off
power switch ON  -> eFuse enabled  -> SYS_5V on
```

Recommended first schematic:

- Use a connector footprint for a latching illuminated panel pushbutton.
- Switch connects the eFuse enable/UVLO network to a valid ON/OFF state.
- Add a defined pull-down or pull-up so `SYS_EN` never floats.
- Add a test point on `SYS_EN`.
- Drive the switch illumination from `SYS_5V` through the appropriate resistor/LED pins so the power button lights only when the protected rail is on.

Whether this is direct enable or an enable/UVLO divider depends on the exact TPS259531 application circuit you choose from the datasheet.

Recommended first-pass switch connector:

Use the panel-mounted NKK `UB216KKG015C` latching illuminated switch connected by a 4-pin harness.

Locked UB2 details:

- SPDT, On-On, alternate-action/latching.
- Gold contacts, 0.4 VA logic-level rating.
- Panel mount / snap-in, solder lug.
- Red LED, nominal forward voltage 1.85 V.
- Cap/legend accessory still needs to be confirmed; plain `UB216KKG015C` may be the switch body/plunger rather than the final visible cap kit.

| Pin | Net | Purpose |
|---:|---|---|
| 1 | `USB_VBUS` | Input to switch contact. |
| 2 | `SYS_EN_SW` | Switched output from latching contact. |
| 3 | `SYS_5V` | LED anode supply, so illumination turns on only after eFuse output is alive. |
| 4 | `GND` | LED cathode return. |

Enable wiring:

```text
USB_VBUS -> switch contact pin 1
switch contact pin 2 -> R_EN_SER 10 kΩ -> SYS_EN / TPS2595 EN/UVLO
SYS_EN -> R_EN_PD 100 kΩ -> GND
```

Power-button LED wiring:

```text
SYS_5V -> R_PWR_LED -> switch LED anode
switch LED cathode -> GND
```

Use the switch LED nominal forward voltage to set `R_PWR_LED`.

Recommended first value:

```text
R_PWR_LED = (5 V - 1.85 V) / 2 mA = 1.575 kΩ
```

Use:

```text
R_PWR_LED = 1.6 kΩ, 0603, 1%, 0.1 W
```

This gives about 2 mA LED current. If the button is too dim in the actual enclosure, reduce to 1.2 kΩ for about 2.6 mA or 1.0 kΩ for about 3.15 mA.

### 2.7.1 Test Points

Recommended physical test point part:

- `Harwin S1751-46R`, SMT loop test point, 3.25 mm x 1.63 mm, 2.0 mm height.

Use this for power and bring-up nets where you may want to clip a probe:

- `TP_USB_VBUS`
- `TP_SYS_5V`
- `TP_SYS_EN`
- `TP_EFUSE_FLT`
- `TP_GND`

For dense signal-only nets later, a plain exposed copper pad is also acceptable. For this first power sheet, use real loop test points because they are easier to clip during bring-up.

### 2.8 Sheet Ports

Export these ports from Group 1:

| Port | Direction | Notes |
|---|---|---|
| `SYS_5V` | Output | Protected 5 V rail to all other sheets. |
| `USB_D_P` | Bidirectional | To ESP32 GPIO20. |
| `USB_D_N` | Bidirectional | To ESP32 GPIO19. |
| `EFUSE_FLT` | Output | To ESP32/test pad, optional. |
| `SYS_EN` | Local/output | Test/debug net. |
| `GND` | Power | Global/reference. |

### 2.9 Group 1 Review Checklist

Before moving to Group 2:

- `CC1` and `CC2` each have 5.1 kΩ to GND.
- `USB_D_P` and `USB_D_N` go through/near ESD and are available as ports to ESP32.
- eFuse input is raw `USB_VBUS`.
- eFuse output is only `SYS_5V`, not accidentally shorted to `USB_VBUS`.
- `SYS_EN` cannot float.
- `EFUSE_FLT` has a sensible pull-up/test strategy.
- Current-limit and dVdt components are present, even if values are still marked TBD.
- There are test points for `USB_VBUS`, `SYS_5V`, `SYS_EN`, `EFUSE_FLT`, and `GND`.
- USB shield strategy is represented with a placeholder footprint/network.

## 3. What We Solve Next

After Group 1 is drawn, Group 2 is the `SYS_5V` to `SYS_3V3` buck regulator:

```text
SYS_5V -> AP63203WU-7 -> SYS_3V3
```

That group will define the 3.3 V rail used by the ESP32, display logic, touch, scanner level shifter, and HMI logic.

## 5. Group 2 - 3.3 V Buck Regulator

### 5.1 Goal

Create the main 3.3 V logic rail:

```text
SYS_5V
  -> AP63203WU-7 buck regulator
  -> SYS_3V3
```

Use the Diodes Inc. AP63203 datasheet values as the first-pass reference. The AP63203WU-EVM is still useful for layout style, but its 6.8 µH / 5 A inductor is mechanically conservative for this fixed 5 V-to-3.3 V design.

### 5.2 Components

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `U_3V3` | Buck regulator | `AP63203WU-7` | Fixed 3.3 V, 2 A, TSOT26. |
| `L_3V3` | Power inductor | 3.9 µH, shielded, Isat >= 3.5 A, Irms >= 2.5 A, low DCR | Datasheet value for AP63203 fixed 3.3 V output. Practical compact alternate: Bourns `SRP4020TA-3R3M` or TDK `SPM4020T-3R3M-LR`, both 3.3 µH shielded 4 mm class parts. |
| `C_BOOT` | Bootstrap cap | 100 nF, X7R, 50 V, 0603, 10% | From `BST` to `SW`, close to IC. |
| `C_IN_3V3_1` | Input bulk | 10 µF, X5R/X7R, 25 V or 35 V, 1206, 10-20% | From `SYS_5V` to GND, close to VIN. EVM uses 35 V/1206. |
| `C_IN_3V3_2` | Input decoupling | 100 nF, X7R, 50 V, 0603, 10% | From `SYS_5V` to GND, very close to VIN/GND. |
| `C_OUT_3V3_1` | Output bulk | 22 µF, X5R/X7R, 16 V or 25 V, 1206, 10-20% | From `SYS_3V3` to GND, near inductor/output. |
| `C_OUT_3V3_2` | Output bulk | 22 µF, X5R/X7R, 16 V or 25 V, 1206, 10-20% | Second output cap, EVM uses two. |
| `R_EN_3V3` | Enable pull-up | 100 kΩ, 0603, 1%, 0.1 W | Pull AP63203 EN to `SYS_5V`. |
| `TP_3V3` | Test point | Harwin `S1751-46R` | Main 3.3 V rail test point. |
| `TP_SW` | Test point or small pad | Small exposed pad only | Optional, for oscilloscope. Do not make it large. |

### 5.3 AP63203 Pin Wiring

AP63203 TSOT26 pinout:

| Pin | Name | Connect To |
|---:|---|---|
| 1 | `FB` | `SYS_3V3` sense node after inductor. |
| 2 | `EN` | `SYS_5V` through `R_EN_3V3 = 100 kΩ`. |
| 3 | `VIN` | `SYS_5V`. |
| 4 | `GND` | Power ground. |
| 5 | `SW` | Switching node to `L_3V3` and `C_BOOT`. |
| 6 | `BST` | `C_BOOT` to `SW`. |

### 5.4 Buck Wiring

Core power path:

```text
SYS_5V -> AP63203 VIN
AP63203 SW -> L_3V3 -> SYS_3V3
SYS_3V3 -> AP63203 FB
```

Bootstrap:

```text
BST -> C_BOOT 100 nF -> SW
```

Input caps:

```text
SYS_5V -> C_IN_3V3_1 10 µF -> GND
SYS_5V -> C_IN_3V3_2 100 nF -> GND
```

Output caps:

```text
SYS_3V3 -> C_OUT_3V3_1 22 µF -> GND
SYS_3V3 -> C_OUT_3V3_2 22 µF -> GND
```

Enable:

```text
SYS_5V -> R_EN_3V3 100 kΩ -> AP63203 EN
```

The eFuse already controls whether `SYS_5V` exists, so this buck can simply auto-enable when `SYS_5V` is present.

### 5.5 Layout Notes

- Keep `VIN` input caps close to the AP63203 VIN/GND pins.
- Keep the `SW` node small. It is noisy.
- Place `C_BOOT` very close to `BST` and `SW`.
- Place `L_3V3` close to `SW`, but keep the high-current switching loop compact.
- Prefer a compact shielded inductor in roughly the 4 mm to 5 mm class. The 6.8 µH / 5 A EVM inductor works electrically, but is larger than needed here.
- Put output caps near the inductor/output side.
- Route FB as a quiet sense trace from the `SYS_3V3` output cap side, not from the noisy `SW` side.
- Do not route sensitive signals under/near the `SW` node.
- Give the buck a solid ground return and stitching vias near caps.

### 5.6 Group 2 Review Checklist

Before moving to Group 3:

- `SYS_5V` feeds VIN and the input caps.
- `SW` only connects to the inductor and bootstrap cap.
- `BST` only connects to bootstrap cap.
- Inductor output net is `SYS_3V3`.
- `FB` connects to `SYS_3V3`, preferably at the output-cap side.
- `EN` is pulled up to `SYS_5V`.
- There are two output caps on `SYS_3V3`.
- There is a real `SYS_3V3` test point and at least one nearby GND test point.
- Values include capacitor dielectric, voltage, package, and tolerance.

## 6. Group 3 - ESP32-S3 Core

### 6.1 Goal

Connect the main MCU module, reset/boot circuitry, USB programming/debug path, and the core test points:

```text
SYS_3V3 -> ESP32-S3-WROOM-1U-N16R8
USB_D_P / USB_D_N -> ESP32 native USB Serial/JTAG
GPIO0 + EN -> manual boot/reset control
```

The selected module is `ESP32-S3-WROOM-1U-N16R8`: external antenna connector, 16 MB flash, 8 MB Octal PSRAM.

### 6.2 Components

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `U_MCU` | MCU module | `ESP32-S3-WROOM-1U-N16R8` | 3.3 V module with U.FL/I-PEX antenna connector. |
| `C_MCU_BULK` | Local MCU bulk | 22 uF, X5R/X7R, 10 V or 16 V, 0805 or 1206, 20% | From `SYS_3V3` to GND, close to module 3V3 pin. |
| `C_MCU_HF` | Local MCU bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | From `SYS_3V3` to GND, very close to module 3V3 pin. |
| `R_MCU_EN` | EN pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull `MCU_EN` to `SYS_3V3`. |
| `C_MCU_EN` | EN delay cap | 1 uF, X7R, 10 V or 16 V, 0603, 10% | From `MCU_EN` to GND. Espressif recommended RC delay value. |
| `SW_RESET` | Reset button | Momentary normally-open tact or test-pad jumper | Pulls `MCU_EN` to GND. Optional but recommended for bring-up. |
| `R_BOOT` | GPIO0 pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull `BOOT_MODE`/GPIO0 to `SYS_3V3`. |
| `SW_BOOT` | Boot button | Momentary normally-open tact or test-pad jumper | Pulls GPIO0 to GND for download mode. Do not add a large cap on GPIO0. |
| `R_GPIO45_PD` | Strap pulldown | 10 k ohm, 0603, 1%, 0.1 W, optional/fitted | Keeps GPIO45 low for default 3.3 V VDD_SPI behavior. |
| `R_GPIO46_PD` | Strap pulldown | 10 k ohm, 0603, 1%, 0.1 W, optional/fitted | Keeps GPIO46 low for deterministic download mode when GPIO0 is held low. |
| `R_USB_DN` | USB series resistor | 22 ohm, 0603, 1%, 0.1 W | Place near ESP32 GPIO19. |
| `R_USB_DP` | USB series resistor | 22 ohm, 0603, 1%, 0.1 W | Place near ESP32 GPIO20. |
| `C_USB_DN_DNP` | USB tuning cap | C0G/NP0, 50 V, 0402/0603, DNP | Footprint from USB D- to GND, close to ESP32 side. |
| `C_USB_DP_DNP` | USB tuning cap | C0G/NP0, 50 V, 0402/0603, DNP | Footprint from USB D+ to GND, close to ESP32 side. |

### 6.2.1 Passive Placement

Place the MCU support passives by function, not by visual grouping:

| Passive | Electrical Location | Physical Placement |
|---|---|---|
| `C_MCU_HF` | `SYS_3V3` to GND | Closest capacitor to module pin 2 `3V3`. Same side as module if possible, with the shortest direct trace to pin 2 and a ground via beside the capacitor ground pad. |
| `C_MCU_BULK` | `SYS_3V3` to GND | Next to `C_MCU_HF`, still close to pin 2. It can be slightly farther away than the 100 nF cap. |
| `R_MCU_EN` | `SYS_3V3` to `MCU_EN` | Close to module pin 3 `EN`. The EN node should be short and quiet. |
| `C_MCU_EN` | `MCU_EN` to GND | Close to module pin 3 `EN`, beside `R_MCU_EN`, with a nearby ground via. |
| `SW_RESET` | `MCU_EN` to GND | Can be near the board edge or debug area. It does not need to be right beside the module, but route it away from the buck `SW` node. |
| `R_BOOT` | `SYS_3V3` to GPIO0 | Close to module pin 27 `IO0`. This resistor defines the strap state, so keep it at the MCU end, not at a remote button. |
| `SW_BOOT` | GPIO0 to GND | Can be near the debug area or board edge. No capacitor on GPIO0. |
| `R_GPIO45_PD` | GPIO45 to GND | Close to module pin 26 `IO45`; optional/fitted. Do not route GPIO45 to external circuitry. |
| `R_GPIO46_PD` | GPIO46 to GND | Close to module pin 16 `IO46`; optional/fitted. Do not route GPIO46 to external circuitry. |
| `R_USB_DN` | Series in USB D- | Close to module pin 13 `IO19`, on the ESP32 side of the USB pair. |
| `R_USB_DP` | Series in USB D+ | Close to module pin 14 `IO20`, side-by-side with `R_USB_DN`, same orientation and spacing. |
| `C_USB_DN_DNP` | USB D- to GND | Optional DNP footprint on the MCU side of `R_USB_DN`, with very short stub and nearby ground via. |
| `C_USB_DP_DNP` | USB D+ to GND | Optional DNP footprint on the MCU side of `R_USB_DP`, symmetric with D-. |

### 6.3 Core Pin Wiring

| Module Pin | Name | Connect To |
|---:|---|---|
| 1 | `GND` | GND. |
| 2 | `3V3` | `SYS_3V3`, with `C_MCU_BULK` and `C_MCU_HF` close by. |
| 3 | `EN` | `MCU_EN`; pull up with 10 k ohm, cap to GND with 1 uF, reset button to GND. |
| 13 | `IO19` | `USB_D_N` through `R_USB_DN = 22 ohm`. |
| 14 | `IO20` | `USB_D_P` through `R_USB_DP = 22 ohm`. |
| 15 | `IO3` | Reserved strapping/JTAG-source pin. No load except optional test pad. |
| 16 | `IO46` | Reserved strapping pin. Add optional/fitted 10 k ohm pulldown to GND. |
| 26 | `IO45` | Reserved strapping pin. Add optional/fitted 10 k ohm pulldown to GND. |
| 27 | `IO0` | `BOOT_MODE`; 10 k ohm pull-up to `SYS_3V3`, boot button to GND. |
| 28, 29, 30 | `IO35`, `IO36`, `IO37` | No-connect. Not available on `N16R8` because of Octal PSRAM. |
| 36, 37 | `RXD0`, `TXD0` | Optional test pads only unless you decide to keep UART0 hardware debug. USB Serial/JTAG is the primary debug path. |
| 40 | `GND` | GND. |
| 41 | `EPAD` | GND copper. Soldering is optional per Espressif, but connecting it improves thermal/grounding behavior. |

All other GPIOs follow [pinout-and-connectors.md](pinout-and-connectors.md).

### 6.4 Reset And Boot Wiring

Normal boot:

```text
GPIO0 = high
EN    = high
```

Manual reset:

```text
SW_RESET pressed -> MCU_EN pulled to GND
```

Manual USB/UART download mode:

```text
hold SW_BOOT -> GPIO0 low
tap SW_RESET -> EN low then high
release SW_BOOT after bootloader starts
```

Recommended schematic:

```text
SYS_3V3 -> R_MCU_EN 10 k ohm -> MCU_EN
MCU_EN -> C_MCU_EN 1 uF -> GND
MCU_EN -> SW_RESET -> GND

SYS_3V3 -> R_BOOT 10 k ohm -> BOOT_MODE / GPIO0
BOOT_MODE / GPIO0 -> SW_BOOT -> GND
```

### 6.5 USB Wiring To MCU

Group 1 already contains the USB-C connector and ESD device. In this group, add the ESP32-side series resistors:

```text
USB_D_N_FROM_ESD -> R_USB_DN 22 ohm -> ESP32 GPIO19 / USB_D-
USB_D_P_FROM_ESD -> R_USB_DP 22 ohm -> ESP32 GPIO20 / USB_D+
```

Add DNP tuning capacitor footprints from each USB line to GND near the ESP32 side:

```text
USB_D_N_MCU -> C_USB_DN_DNP -> GND
USB_D_P_MCU -> C_USB_DP_DNP -> GND
```

Leave these capacitors unpopulated unless EMC/USB testing says otherwise.

### 6.6 Antenna / RF Notes

Because this is the `1U` module, the antenna connector is already on the module. You do not need to design the RF matching network on the main PCB.

Still do these mechanically:

- Keep metal, large copper pours, USB connector shells, inductors, and dense wiring away from the external antenna.
- Put the adhesive/FPC antenna in plastic space, not directly against a metal fridge surface.
- Keep the U.FL/I-PEX coax short and strain-relieved.
- Add an enclosure feature that fixes antenna location repeatably.

### 6.7 Group 3 Review Checklist

Before moving to Group 4:

- Module pin 2 is on `SYS_3V3`, not `SYS_5V`.
- `C_MCU_BULK` and `C_MCU_HF` are close to the module 3V3/GND pins.
- EN has 10 k ohm pull-up, 1 uF cap to GND, and reset button/test pads.
- GPIO0 has 10 k ohm pull-up and boot button/test pads to GND.
- GPIO45 and GPIO46 are not driven by application circuitry.
- GPIO35/GPIO36/GPIO37 are left no-connect for the `N16R8` module.
- USB D- reaches GPIO19 through 22 ohm near the module.
- USB D+ reaches GPIO20 through 22 ohm near the module.
- USB D+/D- still route as a 90 ohm differential pair as much as practical.
- There are test points for `SYS_3V3`, GND, `MCU_EN`, `BOOT_MODE`, `USB_D_N`, and `USB_D_P`.

## 7. Group 4 - Display, Touch, And Backlight

### 7.1 Goal

Connect the Newhaven TFT, capacitive touch panel, and LED backlight driver:

```text
ESP32 8-bit I80 bus -> 40-pin TFT FFC
ESP32 I2C bus       -> 6-pin CTP FFC
SYS_5V              -> STCS1A current driver -> TFT backlight
```

Use the current 2025 Newhaven `NHD-2.8-240320AF-CSXP-FCTP` datasheet. Newhaven revised this display to add SPI support, EMI shielding, and a brighter 160 mA backlight. The 8-bit parallel plan remains valid.

### 7.2 Components

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `J_TFT` | TFT FFC | Molex `54132-4062` or equivalent | 40-pin, 0.5 mm pitch FFC/ZIF. |
| `J_CTP` | Touch FFC | Molex `52271-0679` or equivalent | 6-pin, 1.0 mm pitch FFC/ZIF. |
| `C_TFT_VDD_HF` | TFT bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | Near pins 7/8 and GND. |
| `C_TFT_VDD_BULK` | TFT bulk | 1 uF, X7R, 10 V or 16 V, 0603/0805, 10% | Near 40-pin FFC. 4.7 uF is a fine upgrade if the footprint/BOM allows. |
| `C_CTP_VDD_HF` | Touch bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | Near 6-pin FFC. |
| `C_CTP_VDD_BULK` | Touch bulk | 1 uF, X7R, 10 V or 16 V, 0603/0805, 10% | Near 6-pin FFC. |
| `R_I2C_SCL_PU` | I2C pull-up | 4.7 k ohm, 0603, 1%, 0.1 W | One shared pull-up on main PCB. |
| `R_I2C_SDA_PU` | I2C pull-up | 4.7 k ohm, 0603, 1%, 0.1 W | One shared pull-up on main PCB. |
| `R_DISP_RST_PU` | Reset pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull `DISP_TOUCH_RST` high. |
| `R_TOUCH_INT_PU` | Touch interrupt pull-up | 10 k ohm, 0603, 1%, 0.1 W, optional/fitted | Provision for touch `/INT`. |
| `U_BL` | Backlight driver | `STCS1APUR` | STCS1A, DFN8 3 mm x 3 mm. |
| `R_BL_SET` | Backlight current set | 0.68 ohm, 1%, 1206, >=0.25 W, low TCR preferred | About 147 mA typical. Use 0.62 ohm for about 160 mA. |
| `C_BL_VCC_HF` | Driver bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | Close to STCS1A VCC/GND. |
| `C_BL_VCC_BULK` | Driver bulk | 1 uF, X7R, 16 V or 25 V, 0603/0805, 10% | Local to STCS1A. |
| `C_BL_DRAIN` | Drain capacitor | 470 nF, X7R, 10 V or 16 V, 0603/0805, 10% | From STCS1A `DRAIN` / display LED cathode node to GND. |
| `C_BL_SLOPE` | Slope cap | 10 nF, C0G/NP0 or X7R, 50 V, 0603, 5-10% | Controls current rise/fall slope. |
| `R_BL_PWM_PD` | PWM pulldown | 100 k ohm, 0603, 1%, 0.1 W | Keeps backlight off during reset/boot. |
| `R_BL_EN` | EN pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull STCS1A EN high to `SYS_5V`. |

### 7.3 TFT 40-Pin FFC Wiring

Use 8-bit 8080-II parallel mode: `IM0 = 1`, `IM1 = 0`, `IM2 = 0`.

| TFT Pin | Symbol | Connect To |
|---:|---|---|
| 1 | `GND` | GND. |
| 2-5 | `NC` | No connect. |
| 6 | `SDO` | No connect for 8-bit parallel. Optional test pad only. |
| 7 | `VDD` | `SYS_3V3`. |
| 8 | `VDDI` | `SYS_3V3`. |
| 9 | `SDA` | No connect for 8-bit parallel/SPI data input not used. |
| 10 | `CSX` | `LCD_CS` / ESP32 GPIO14. |
| 11 | `DCX` | `LCD_DC` / ESP32 GPIO13. |
| 12 | `WRX` | `LCD_WR` / ESP32 GPIO12. |
| 13 | `RDX` | Pull high to `SYS_3V3` with 10 k ohm if readback is not used. |
| 14-21 | `DB0`-`DB7` | No connect in 8-bit mode. |
| 22 | `DB8` | `LCD_D0` / ESP32 GPIO4. |
| 23 | `DB9` | `LCD_D1` / ESP32 GPIO5. |
| 24 | `DB10` | `LCD_D2` / ESP32 GPIO6. |
| 25 | `DB11` | `LCD_D3` / ESP32 GPIO7. |
| 26 | `DB12` | `LCD_D4` / ESP32 GPIO8. |
| 27 | `DB13` | `LCD_D5` / ESP32 GPIO9. |
| 28 | `DB14` | `LCD_D6` / ESP32 GPIO10. |
| 29 | `DB15` | `LCD_D7` / ESP32 GPIO11. |
| 30 | `/RES` | `DISP_TOUCH_RST` / ESP32 GPIO15, with 10 k ohm pull-up to `SYS_3V3`. |
| 31 | `IM0` | Pull high to `SYS_3V3` with 10 k ohm. |
| 32 | `IM1` | Pull low to GND with 10 k ohm. |
| 33 | `IM2` | Pull low to GND with 10 k ohm. |
| 34-37 | `LED-K1`-`LED-K4` | Tie together as `BL_LED_K`; connect to STCS1A `DRAIN`. Do not tie directly to GND. |
| 38 | `LED-A` | `BL_LED_A`; connect to `SYS_5V` / backlight supply. |
| 39 | `GND` | GND. |
| 40 | `TE` | Optional test pad only; otherwise no connect. |

### 7.4 Touch 6-Pin FFC Wiring

| CTP Pin | Symbol | Connect To |
|---:|---|---|
| 1 | `VDD` | `SYS_3V3`, with local `C_CTP_VDD_HF` and `C_CTP_VDD_BULK`. |
| 2 | `VSS` | GND. |
| 3 | `SCL` | `I2C_SCL` / ESP32 GPIO17, with one 4.7 k ohm pull-up to `SYS_3V3`. |
| 4 | `SDA` | `I2C_SDA` / ESP32 GPIO18, with one 4.7 k ohm pull-up to `SYS_3V3`. |
| 5 | `/INT` | `TOUCH_INT` / ESP32 GPIO21, with 10 k ohm pull-up provision. |
| 6 | `/RESET` | `DISP_TOUCH_RST` / ESP32 GPIO15. Do not tie directly to VCC. |

### 7.5 STCS1A Backlight Wiring

Set a slightly conservative backlight current first:

```text
I_LED = 100 mV / R_BL_SET
R_BL_SET = 0.68 ohm -> about 147 mA typical
```

STCS1A wiring:

| STCS1A Pin | Name | Connect To |
|---:|---|---|
| 1 | `VCC` | `SYS_5V`, with `C_BL_VCC_HF` and `C_BL_VCC_BULK` close. |
| 2 | `PWM` | `LCD_BL_PWM` / ESP32 GPIO16 through optional 100 ohm series resistor; add 100 k ohm pulldown to GND. |
| 3 | `EN` | Pull high to `SYS_5V` with 10 k ohm. |
| 4 | `DRAIN` | `BL_LED_K` / TFT pins 34-37. Add `C_BL_DRAIN` from this node to GND. |
| 5 | `FB` | `BL_SENSE`; connect only to `R_BL_SET` to GND. Do not tie directly to the display LED pins. |
| 6 | `GND` | GND. |
| 7 | `SLOPE` | `C_BL_SLOPE` to GND. |
| 8 | `DISC` | Optional test pad or 10 k ohm pull-up to `SYS_3V3`; no MCU GPIO required in v1. |
| EPAD | exposed pad | GND copper with thermal vias. |

### 7.6 Placement Notes

- Put `J_TFT` and `J_CTP` according to the mechanical display flex exits first; the enclosure will depend on this.
- Keep `C_TFT_VDD_HF`, `C_TFT_VDD_BULK`, `C_CTP_VDD_HF`, and `C_CTP_VDD_BULK` close to their FFC connectors.
- Put the STCS1A close to the TFT backlight pins, not next to the ESP32.
- Keep the `DRAIN`/`BL_LED_K` and `FB`/`BL_SENSE` current loop compact.
- Give STCS1A exposed pad real GND copper; it will dissipate roughly a few hundred milliwatts at full brightness.
- Keep the I2C lines away from the backlight current loop and the buck `SW` node.
- Add small signal test pads for `LCD_WR`, `LCD_DC`, `LCD_CS`, `DISP_TOUCH_RST`, `I2C_SCL`, `I2C_SDA`, `TOUCH_INT`, and `LCD_BL_PWM`.

### 7.7 Group 4 Review Checklist

Before moving to Group 5:

- TFT pins 7 and 8 are on `SYS_3V3`, not `SYS_5V`.
- TFT pins 22-29 connect to `LCD_D0`-`LCD_D7`; pins 14-21 are not used in 8-bit mode.
- `RDX` is held high if readback is unused.
- `IM0=1`, `IM1=0`, `IM2=0`.
- TFT `/RES` and CTP `/RESET` are controlled by `DISP_TOUCH_RST`; touch reset is not tied directly to VCC.
- I2C has one pull-up pair on the main PCB, 4.7 k ohm to `SYS_3V3`.
- Backlight current path is `SYS_5V -> LED-A -> LED-K -> STCS1A DRAIN -> internal MOSFET -> FB -> R_BL_SET -> GND`.
- Backlight current is set by `R_BL_SET`; LED-K pins are not tied directly to GND.
- STCS1A thermal pad is connected to GND copper.

## 8. Group 5 - Scanner Interface

### 8.1 Goal

Connect the Waveshare scanner as a switched 5 V peripheral with a UART interface that is safe for the ESP32:

```text
SYS_5V -> TPS22919 load switch -> SCANNER_5V -> scanner connector
ESP32 UART 3.3 V <-> TXU0202 <-> scanner UART side
```

The scanner family is easy to integrate, but its UART voltage is not something we should trust blindly. Keep the level shifter in v1.

### 8.2 Components

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `J_SCAN` | Scanner connector | JST-PH `B4B-PH-K-S` or matching Waveshare cable connector | 4-pin, 2.0 mm. Confirm pin order against exact module silk/official pinout. |
| `U_SCAN_SW` | Load switch | `TPS22919DCKR` | 5.5 V, 1.5 A load switch with controlled rise time and short protection. |
| `C_SCAN_IN` | Load switch input bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | From `SYS_5V` to GND, close to TPS22919 IN/GND. |
| `C_SCAN_OUT_HF` | Scanner output bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | From `SCANNER_5V` to GND near connector. |
| `C_SCAN_OUT_BULK` | Scanner output bulk | 10 uF, X5R/X7R, 16 V or 25 V, 0805/1206, 10-20% | From `SCANNER_5V` to GND near connector. |
| `R_SCAN_SW_PD` | Load switch ON pulldown | 100 k ohm, 0603, 1%, 0.1 W | Keeps scanner off during ESP32 reset/boot. |
| `U_SCAN_LVL` | UART level shifter | `TXU0202DCUR` | Fixed direction, dual-supply translator; one UART channel each way. |
| `C_SCAN_LVL_A` | TXU0202 VCCA bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | VCCA to GND, close to IC. |
| `C_SCAN_LVL_B` | TXU0202 VCCB bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | VCCB to GND, close to IC. |
| `R_SCAN_OE` | TXU0202 enable pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull OE to `SYS_3V3`. |
| `R_SCAN_TX_SER` | UART series resistor | 100 ohm, 0603, 1%, 0.1 W | Scanner TX into translator. |
| `R_SCAN_RX_SER` | UART series resistor | 100 ohm, 0603, 1%, 0.1 W | Translator output to scanner RX. |
| `TP_SCANNER_5V` | Scanner power test point | Harwin loop or 1 mm pad | Useful during bring-up. |
| `TP_SCAN_TX`, `TP_SCAN_RX` | UART test pads | 0.8-1.0 mm bare pads | Place on ESP32-side UART nets. |

### 8.3 Scanner Connector Pin Order

Do not guess the connector pin order from the PH2.0 family or cable colors.

For Waveshare `Barcode Scanner Module (E)`, the official wiki pinout is:

| Module Pin | Module Signal | Main PCB Net |
|---:|---|---|
| 1 | `GND` | GND |
| 2 | `RX` | `SCAN_RX_TO_MODULE` |
| 3 | `TX` | `SCAN_TX_FROM_MODULE` |
| 4 | `VCC` | `SCANNER_5V` |

For the older Waveshare `Barcode Scanner Module` SKU 14810, verify the board silk before locking the footprint. Its quick-start guide says to connect by `VCC`, `GND`, `RX`, and `TX` labels.

UART naming convention:

```text
SCAN_RX_TO_MODULE   = data from ESP32 TX into scanner RX
SCAN_TX_FROM_MODULE = data from scanner TX into ESP32 RX
```

### 8.4 TPS22919 Load Switch Wiring

TPS22919 pin wiring:

| Pin | Name | Connect To |
|---:|---|---|
| 1 | `IN` | `SYS_5V`, with `C_SCAN_IN` nearby. |
| 2 | `GND` | GND. |
| 3 | `ON` | `SCANNER_PWR_EN` / ESP32 GPIO38, with `R_SCAN_SW_PD` to GND. |
| 4 | `NC` | No connect. |
| 5 | `QOD` | Tie to `SCANNER_5V` to discharge scanner rail when off. |
| 6 | `VOUT` | `SCANNER_5V`, with local output capacitors. |

Power path:

```text
SYS_5V -> TPS22919 IN
TPS22919 VOUT -> SCANNER_5V -> scanner VCC
SCANNER_PWR_EN high -> scanner powered
SCANNER_PWR_EN low  -> scanner off, QOD discharges SCANNER_5V
```

### 8.5 TXU0202 UART Level Shifter Wiring

Use `TXU0202DCUR` with `VCCA = SYS_3V3` and `VCCB = SCANNER_5V`.

TXU0202 pin wiring:

| Pin | Name | Connect To |
|---:|---|---|
| 1 | `B2` | Scanner-side TX input: `SCAN_TX_FROM_MODULE` through `R_SCAN_TX_SER = 100 ohm`. |
| 2 | `GND` | GND. |
| 3 | `VCCA` | `SYS_3V3`, with `C_SCAN_LVL_A`. |
| 4 | `A2Y` | ESP32-side RX: `MCU_SCAN_RX` / GPIO2. |
| 5 | `A1` | ESP32-side TX: `MCU_SCAN_TX` / GPIO1. |
| 6 | `OE` | `SYS_3V3` through `R_SCAN_OE = 10 k ohm`. |
| 7 | `VCCB` | `SCANNER_5V`, with `C_SCAN_LVL_B`. |
| 8 | `B1Y` | Scanner-side RX output: `SCAN_RX_TO_MODULE` through `R_SCAN_RX_SER = 100 ohm`. |

Signal paths:

```text
ESP32 GPIO1 / MCU_SCAN_TX -> TXU0202 A1 -> B1Y -> scanner RX
scanner TX -> TXU0202 B2 -> A2Y -> ESP32 GPIO2 / MCU_SCAN_RX
```

When `SCANNER_5V` is off, TXU0202 VCC isolation disables the outputs, which helps avoid back-powering the scanner.

### 8.6 Placement Notes

- Put `U_SCAN_SW` near the scanner connector if possible; keep the switched 5 V loop compact.
- Place `C_SCAN_OUT_HF` and `C_SCAN_OUT_BULK` near `J_SCAN`, because the scanner current pulses happen there.
- Put `U_SCAN_LVL` near the scanner connector or between connector and ESP32 routing, whichever gives shorter UART stubs.
- Keep UART test pads on the ESP32-side nets: `MCU_SCAN_TX` and `MCU_SCAN_RX`.
- Add a real power test point for `SCANNER_5V`; this is useful when testing sleep/wake and scanner power cycling.
- If the scanner cable is long or exposed to handling, add optional low-cap ESD protection footprints on the UART lines near `J_SCAN`.

### 8.7 Group 5 Review Checklist

Before moving to Group 6:

- `SCANNER_5V` is generated through TPS22919, not tied directly to `SYS_5V`.
- TPS22919 `ON` has a defined low state during reset/boot.
- TPS22919 `QOD` is tied to `SCANNER_5V` if you want fast power-off discharge.
- Scanner connector pin numbers match the exact module/cable pinout.
- `VCCA` of TXU0202 is `SYS_3V3`; `VCCB` is `SCANNER_5V`.
- ESP32 TX goes to scanner RX through the A1-to-B1Y TXU0202 channel.
- Scanner TX goes to ESP32 RX through the B2-to-A2Y TXU0202 channel.
- There are test pads for `SCANNER_5V`, `MCU_SCAN_TX`, and `MCU_SCAN_RX`.

## 9. Group 6 - Front-Panel HMI Connector

### 9.1 Goal

Create the main-board connector contract for the separate front-panel PCB:

```text
Main PCB ESP32/I2C/5V/3V3 -> JST-GH 14-pin harness -> UI PCB
```

The UI PCB will contain:

- 8x NKK RGB illuminated buttons.
- 1x `PCAL9555A` I2C GPIO expander for button contacts.
- 1x `TLC5947DAPRG4` LED driver for the 24 RGB LED channels.

This group is only the **main PCB connector side**. The PCAL9555A, TLC5947, and buttons are solved on the front-panel PCB sheet later.

### 9.2 Connector Parts

Use JST GH, 1.25 mm pitch, locking wire-to-board.

| Use | Part | Notes |
|---|---|---|
| Main PCB top-entry header | `BM14B-GHS-TBT(LF)(SN)` or `BM14B-GHS-TBT(LF)(SN)(N)` | 14-position SMT top-entry header. |
| Main PCB side-entry alternate | `SM14B-GHS-TB(LF)(SN)` | Use only if the cable should exit parallel to the main PCB. |
| Cable housing | `GHR-14V-S` | One housing at each end of the harness. |
| Crimp contact | `SSHL-002T-P0.2` | Use AWG 26-30 class wire; choose exact wire gauge after enclosure routing. |

The GH family is rated 1 A class per contact and 50 V class, so duplicated `VLED_5V` and GND pins are more than enough for the button LEDs in this design.

### 9.3 Main PCB Components

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `J_HMI` | HMI connector | `BM14B-GHS-TBT(LF)(SN)` | Top-entry default. Use side-entry only if mechanical design wants it. |
| `R_LED_SIN_SER` | Series resistor | 33 ohm, 0603, 1%, 0.1 W | Place before connector on `LED_SIN`. |
| `R_LED_SCLK_SER` | Series resistor | 33 ohm, 0603, 1%, 0.1 W | Place before connector on `LED_SCLK`. |
| `R_LED_LAT_SER` | Series resistor | 33 ohm, 0603, 1%, 0.1 W | Place before connector on `LED_LAT`. |
| `R_LED_BLANK_SER` | Series resistor | 33 ohm, 0603, 1%, 0.1 W | Place before connector on `LED_BLANK`. |
| `R_HMI_INT_PU` | Interrupt pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull `HMI_INT` to `SYS_3V3` on main PCB. |
| `R_BTN_MULTI_WAKE_PU` | Wake-line pull-up | 10 k ohm, 0603, 1%, 0.1 W | Pull `BTN_MULTI_WAKE` to `SYS_3V3` on main PCB. |
| `C_HMI_3V3_CONN` | Optional connector bypass | 100 nF, X7R, 16 V or 25 V, 0603, 10% | Near `J_HMI` pin 3. Main logic bulk is elsewhere; UI board still needs local caps. |
| `C_HMI_VLED_CONN` | Optional connector bypass | 1 uF, X7R, 16 V or 25 V, 0603/0805, 10% | Near `J_HMI` pins 1/2. UI board still needs LED bulk. |

Do not add another I2C pull-up pair here if the display/touch sheet already has the main shared `4.7 k ohm` pull-ups. There should be one shared I2C pull-up pair on the main PCB.

### 9.4 J_HMI Pinout

| Pin | Net | Direction From Main PCB | Notes |
|---:|---|---|---|
| 1 | `VLED_5V` | Power out | 5 V for NKK RGB LED common anodes. |
| 2 | `VLED_5V` | Power out | Duplicate 5 V pin for current/headroom. Tie to pin 1 on both boards. |
| 3 | `SYS_3V3` | Power out | Logic supply for PCAL9555A and TLC5947 logic. |
| 4 | `GND` | Return | Ground return. |
| 5 | `GND` | Return | Duplicate ground return. |
| 6 | `I2C_SCL` | Output | Shared I2C clock from ESP32 GPIO17. |
| 7 | `I2C_SDA` | Bidirectional | Shared I2C data from ESP32 GPIO18. |
| 8 | `HMI_INT` | Input to main | Open-drain interrupt from PCAL9555A, pulled up on main PCB. |
| 9 | `LED_SIN_HMI` | Output | `LED_SIN` through 33 ohm series resistor. |
| 10 | `LED_SCLK_HMI` | Output | `LED_SCLK` through 33 ohm series resistor. |
| 11 | `LED_LAT_HMI` | Output | `LED_LAT` through 33 ohm series resistor. |
| 12 | `LED_BLANK_HMI` | Output | `LED_BLANK` through 33 ohm series resistor. |
| 13 | `BTN_MULTI_WAKE` | Input to main | Direct multifunction button wake line, active-low. Pull up on main PCB. |
| 14 | `HMI_RESERVED` | Spare | Route to a test pad or leave no-connect. Do not tie to GND unless using as a deliberate key/spare strategy. |

Recommended LED serial signal naming:

```text
ESP32 GPIO39 / LED_SIN   -> R_LED_SIN_SER   -> LED_SIN_HMI   -> J_HMI pin 9
ESP32 GPIO40 / LED_SCLK  -> R_LED_SCLK_SER  -> LED_SCLK_HMI  -> J_HMI pin 10
ESP32 GPIO41 / LED_LAT   -> R_LED_LAT_SER   -> LED_LAT_HMI   -> J_HMI pin 11
ESP32 GPIO42 / LED_BLANK -> R_LED_BLANK_SER -> LED_BLANK_HMI -> J_HMI pin 12
```

### 9.5 Pull-Up Wiring

HMI interrupt:

```text
SYS_3V3 -> R_HMI_INT_PU 10 k ohm -> HMI_INT
HMI_INT -> J_HMI pin 8
HMI_INT -> ESP32 GPIO47
```

Multifunction wake:

```text
SYS_3V3 -> R_BTN_MULTI_WAKE_PU 10 k ohm -> BTN_MULTI_WAKE
BTN_MULTI_WAKE -> J_HMI pin 13
BTN_MULTI_WAKE -> ESP32 GPIO48
```

On the front-panel PCB, the multifunction button contact should short `BTN_MULTI_WAKE` to GND when pressed. It can also connect to one PCAL9555A input so firmware sees it in the normal button matrix.

### 9.6 Placement Notes

- Choose top-entry vs side-entry from the enclosure/cable exit first. Do not change this late; it affects the printed case.
- Place `J_HMI` near the board edge facing the front-panel PCB.
- Put the 33 ohm LED signal resistors on the main PCB before the cable. If the ESP32-to-connector trace is short, placing them near `J_HMI` is fine.
- Keep `VLED_5V` and GND traces wider than logic traces. The RGB LEDs can create visible brightness glitches if the return path is skinny.
- Route `I2C_SCL` and `I2C_SDA` as a pair-ish, away from the backlight DRAIN node and the 3.3 V buck `SW` node.
- Add test pads for `I2C_SCL`, `I2C_SDA`, `HMI_INT`, `BTN_MULTI_WAKE`, `LED_SCLK`, `VLED_5V`, `SYS_3V3`, and GND.

### 9.7 Group 6 Review Checklist

Before moving to Group 7:

- `VLED_5V` uses two connector pins and is not confused with `SYS_3V3`.
- `SYS_3V3` is present on one connector pin for HMI logic only.
- Two GND pins are present.
- There is only one shared I2C pull-up pair on the main PCB.
- `HMI_INT` has a 10 k ohm pull-up to `SYS_3V3`.
- `BTN_MULTI_WAKE` has a 10 k ohm pull-up to `SYS_3V3`.
- LED serial/control lines pass through 33 ohm series resistors before the connector.
- Pin 14 is clearly marked `HMI_RESERVED` or `NC`, not accidentally shorted.
- The connector orientation and pin-1 marking are obvious in the PCB footprint/silkscreen.

## 10. Group 7 - Buzzer And Optional Status LED

### 10.1 Goal

Add a simple audible feedback output for scan success, scan error, and UI acknowledgement:

```text
ESP32 GPIO44 / BUZZER_PWM -> passive piezo transducer -> GND
```

The device already has a display, RGB front-panel buttons, and the illuminated power switch. Do not add a separate normal-use status LED unless you later find you need it. A test pad on `BUZZER_PWM` is enough for bring-up.

### 10.2 Preferred Buzzer

Use a passive piezo transducer:

| Ref | Component | Exact / Suggested Part | Notes |
|---|---|---|---|
| `BZ1` | Passive piezo transducer | TDK `PS1240P02BT` | 3 V rated, 4 kHz, through-hole, externally driven. |
| `R_BUZZ_SER` | Series resistor | 100 ohm, 0603, 1%, 0.1 W | Between ESP32 and piezo positive terminal. |
| `R_BUZZ_BLEED` | Bleed resistor | 1 Mohm, 0603, 1%, 0.1 W | Across piezo terminals. |
| `TP_BUZZER_PWM` | Test pad | 0.8-1.0 mm bare pad | On ESP32-side `BUZZER_PWM`. |

No MOSFET and no flyback diode are needed for this selected passive piezo.

### 10.3 Wiring

ESP32 module pin:

```text
ESP32 GPIO44 / RXD0 / module pin 36 -> BUZZER_PWM
```

Buzzer circuit:

```text
BUZZER_PWM -> R_BUZZ_SER 100 ohm -> BUZZER_DRIVE -> BZ1 pin 1
BZ1 pin 2 -> GND
BUZZER_DRIVE -> R_BUZZ_BLEED 1 Mohm -> GND
```

This is firmware-controlled with LEDC/PWM. Start testing around 4 kHz because the selected piezo is specified at 4 kHz.

### 10.4 Optional Connector Variant

If enclosure acoustics make it better to mount the piezo away from the main PCB, replace or supplement `BZ1` with a 2-pin connector:

| Pin | Net | Notes |
|---:|---|---|
| 1 | `BUZZER_DRIVE` | From `R_BUZZ_SER`. |
| 2 | `GND` | Return. |

Use a small locking connector if cabled. Keep the cable short; this is a PWM signal.

### 10.5 If You Later Want A Louder Buzzer

If the passive piezo is too quiet in the enclosure, do not try to pull heavy current from the ESP32 pin. Change the block to a 5 V active buzzer with an N-MOSFET low-side driver:

```text
SYS_5V -> active buzzer + terminal
active buzzer - terminal -> NMOS drain
NMOS source -> GND
BUZZER_PWM -> 100 ohm -> NMOS gate
NMOS gate -> 100 k ohm -> GND
```

For an active magnetic buzzer or any inductive buzzer, add the flyback diode recommended by the buzzer datasheet.

### 10.6 Placement Notes

- Put `BZ1` near an acoustic opening or slot in the enclosure, not under the display or against a sealed wall.
- Leave a small keepout/opening above the sound port.
- Keep the buzzer PWM trace away from touch/I2C if possible.
- Add the `TP_BUZZER_PWM` test pad near the ESP32 side, not necessarily near the buzzer.
- Mark the buzzer polarity if the chosen footprint has a `+` terminal.

### 10.7 Group 7 Review Checklist

Before moving to Group 8:

- `BUZZER_PWM` connects to ESP32 GPIO44/RXD0/module pin 36.
- `R_BUZZ_SER = 100 ohm` is in series with the piezo.
- Piezo second terminal goes to GND.
- `R_BUZZ_BLEED = 1 Mohm` is across the piezo.
- No flyback diode is fitted for the passive piezo version.
- Acoustic opening/placement is considered in the mechanical layout.

## 11. Sources

- TI TPS259531DSGR page: https://www.ti.com/product/TPS2595/part-details/TPS259531DSGR
- ST USBLC6-2 product page: https://www.st.com/en/protections-and-emi-filters/usblc6-2.html
- GCT USB4105-GF-A: https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198441
- Diodes Inc. AP63203: https://www.diodes.com/part/view/AP63203
- AP63203WU-EVM user guide: https://www.digikey.com/en/htmldatasheets/production/3781564/0/0/1/ap63203wu-evm
- Espressif ESP32-S3-WROOM-1/WROOM-1U datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- Espressif ESP32-S3 hardware design guidelines: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html
- Newhaven `NHD-2.8-240320AF-CSXP-FCTP` datasheet: https://newhavendisplay.com/content/specs/NHD-2.8-240320AF-CSXP-FCTP.pdf
- STMicroelectronics `STCS1A` datasheet: https://www.st.com/resource/en/datasheet/stcs1a.pdf
- Waveshare `Barcode Scanner Module (E)` wiki: https://www.waveshare.com/wiki/Barcode_Scanner_Module_%28E%29
- Waveshare `Barcode Scanner Module` quick start: https://files.waveshare.com/upload/3/35/Barcode_Scanner_Module_Quick_Start_EN.pdf
- TI `TPS22919` datasheet: https://www.ti.com/lit/ds/symlink/tps22919.pdf
- TI `TXU0202` datasheet: https://www.ti.com/lit/ds/symlink/txu0202.pdf
- JST GH connector family: https://jst.es/producto/gh-connector/
- DigiKey `BM14B-GHS-TBT(LF)(SN)(N)`: https://www.digikey.com/en/products/detail/jst-sales-america-inc/BM14B-GHS-TBT-LF-SN-N/807812
- DigiKey TDK `PS1240P02BT`: https://www.digikey.com/en/products/detail/tdk/PS1240P02BT/935924
