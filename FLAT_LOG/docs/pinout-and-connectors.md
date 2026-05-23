# Pinout And Connector Plan

This document is the first Altium-ready pin planning pass for the main PCB and front-panel HMI PCB.

## 1. Source Constraints

Target module:

- `ESP32-S3-WROOM-1U-N16R8`
- 16 MB flash
- 8 MB octal PSRAM
- External antenna connector

Important constraints:

- GPIO19 and GPIO20 are reserved for native USB D-/D+ and USB Serial/JTAG.
- GPIO0, GPIO3, GPIO45, and GPIO46 are strapping pins. Avoid user-facing or strongly driven circuitry on these pins.
- GPIO35, GPIO36, and GPIO37 are not available for this design because the selected `N16R8` module uses octal PSRAM.
- GPIO43 and GPIO44 are default UART0 pins. This design prefers USB Serial/JTAG for logs and programming, so UART0 is optional/test only. Avoid using TXD0/GPIO43 for scanner power enable because it may be active during boot.
- GPIO26 through GPIO34 are not exposed on the ESP32-S3-WROOM module footprint.
- EN must not float.

## 2. Pin Allocation Summary

| GPIO | Net / Function | Direction | Sheet / Block | Notes |
|---:|---|---|---|---|
| 0 | BOOT_MODE | Input | Debug | Strapping pin. Use only boot button/test pad with correct pull-up behavior. |
| 1 | MCU_SCAN_TX | Output | Scanner | UART TX from ESP32 to scanner. |
| 2 | MCU_SCAN_RX | Input | Scanner | UART RX into ESP32 from scanner. Add protection/level-shift provision. |
| 3 | RESERVED_STRAP | - | Reserved | Strapping pin. Avoid loading. |
| 4 | LCD_D0 | Output | Display | I80 data bit 0. |
| 5 | LCD_D1 | Output | Display | I80 data bit 1. |
| 6 | LCD_D2 | Output | Display | I80 data bit 2. |
| 7 | LCD_D3 | Output | Display | I80 data bit 3. |
| 8 | LCD_D4 | Output | Display | I80 data bit 4. |
| 9 | LCD_D5 | Output | Display | I80 data bit 5. |
| 10 | LCD_D6 | Output | Display | I80 data bit 6. |
| 11 | LCD_D7 | Output | Display | I80 data bit 7. |
| 12 | LCD_WR | Output | Display | I80 write strobe. |
| 13 | LCD_DC | Output | Display | Data/command select. |
| 14 | LCD_CS | Output | Display | Display chip select. |
| 15 | DISP_TOUCH_RST | Output | Display / Touch | Shared active-low reset for TFT `/RES` and touch `/RESET`. |
| 16 | LCD_BL_PWM | Output | Backlight | Backlight dimming/control input. |
| 17 | I2C_SCL | Output | Touch + HMI | Shared I2C clock for touch controller and front-panel expander. |
| 18 | I2C_SDA | I/O | Touch + HMI | Shared I2C data. |
| 19 | USB_DN | I/O | USB-C | Reserved for native USB D-. |
| 20 | USB_DP | I/O | USB-C | Reserved for native USB D+. |
| 21 | TOUCH_INT | Input | Touch | Capacitive touch interrupt. |
| 35 | NC_PSRAM | - | No connect | Do not use on `N16R8`. |
| 36 | NC_PSRAM | - | No connect | Do not use on `N16R8`. |
| 37 | NC_PSRAM | - | No connect | Do not use on `N16R8`. |
| 38 | SCANNER_PWR_EN | Output | Scanner Power | Controls scanner 5 V load switch. Safer than TXD0/GPIO43 during boot. |
| 39 | LED_SIN | Output | HMI LEDs | TLC5947 serial data. |
| 40 | LED_SCLK | Output | HMI LEDs | TLC5947 serial clock. |
| 41 | LED_LAT | Output | HMI LEDs | TLC5947 latch. |
| 42 | LED_BLANK | Output | HMI LEDs | TLC5947 blank/global enable. |
| 43 | UART0_TX_TP / SCAN_AUX_SPARE | Optional | Debug / Spare | Module pin is labeled `TXD0`; leave as test pad/spare, not scanner power enable. |
| 44 | BUZZER_PWM | Output | Feedback | PWM drive for passive piezo buzzer. Module pin is labeled `RXD0`. |
| 45 | RESERVED_STRAP | - | Reserved | Strapping pin. Avoid loading. |
| 46 | RESERVED_STRAP | - | Reserved | Strapping pin. Avoid loading. |
| 47 | HMI_INT | Input | HMI Buttons | Open-drain interrupt from PCAL9555A front-panel expander. |
| 48 | BTN_MULTI_WAKE | Input | HMI Buttons | Direct wake-capable multifunction button line. |

## 3. Pin Budget Consequence

The 8-bit I80 display is worth keeping for UI polish, but it consumes many GPIOs.

Therefore:

- Do not use direct GPIO for all eight buttons.
- Use a front-panel PCAL9555A-class I2C GPIO expander for button sensing.
- Wire the multifunction button both to the expander and directly to GPIO48 for wake/sleep responsiveness.
- Use TLC5947 for all RGB button LEDs.

This keeps the main PCB pin budget workable and makes the front-panel harness much cleaner.

## 4. Main PCB Connectors

Connector names are provisional. Exact connector series will be selected during schematic/mechanical design.

### J1 - USB-C Input / Programming

| Signal | Notes |
|---|---|
| VBUS | 5 V input. |
| GND | System return. |
| CC1, CC2 | USB-C sink pulldowns. |
| USB_DN | GPIO19 via USB ESD protection. |
| USB_DP | GPIO20 via USB ESD protection. |
| Shield | Chassis/system-ground strategy TBD. |

### J2 - Scanner Module

Baseline scanner: Waveshare Barcode Scanner Module.

| Pin | Signal | Notes |
|---:|---|---|
| 1 | TBD by exact module | Match the Waveshare board silk/official pinout before PCB release. |
| 2 | TBD by exact module | For Barcode Scanner Module (E): module RX, connect to `SCAN_RX_TO_MODULE`. |
| 3 | TBD by exact module | For Barcode Scanner Module (E): module TX, connect to `SCAN_TX_FROM_MODULE`. |
| 4 | TBD by exact module | For Barcode Scanner Module (E): VCC, connect to `SCANNER_5V`. |
| 5 | SCAN_AUX_SPARE | Optional future trigger/control, not exposed on baseline Waveshare 4-pin cable. |
| 6 | SCAN_GOOD_TP | Optional good-read/status test pad or future pin. |
| 7 | 3V3_AUX | Optional logic reference / future scanner variant. |

Design note:

- The Waveshare-supplied cable is listed as PH2.0 4-pin. Use pins 1-4 for the final harness and keep pins 5-7 as pads or alternate connector positions only if you intentionally create a larger alternate footprint.
- Do not infer the 4-pin order from cable colors or generic PH2.0 orientation. Match the exact Waveshare module silk/official pinout.
- GPIO2 input from scanner must be level shifted or protected until scanner UART voltage is confirmed.
- The selected Waveshare module does not expose a hardware trigger/status pin on the documented 4-pin UART cable. Prefer UART/configuration control or sensing/continuous modes.

### J3 - Display TFT FFC

Exact pinout follows the selected Newhaven display datasheet. Use the current 2025 `NHD-2.8-240320AF-CSXP-FCTP` revision; older PDFs for this family do not include the revised SPI-capable FPC pinout and 160 mA backlight.

Connector:

- 40-pin, 0.5 mm pitch FFC/ZIF.
- Recommended datasheet connector: Molex `54132-4062` or similar.
- This connector should be placed directly on the final PCB near the display flex tail.
- The Newhaven `NHD-FFC40` breakout and 2x20 IDC cable are for prototyping, not the preferred final design.

Logical signals:

| Signal | ESP32 GPIO | Notes |
|---|---:|---|
| LCD_D0 | 4 | Connect to Newhaven TFT `DB8` for 8-bit 8080-II mode. |
| LCD_D1 | 5 | Connect to Newhaven TFT `DB9` for 8-bit 8080-II mode. |
| LCD_D2 | 6 | Connect to Newhaven TFT `DB10` for 8-bit 8080-II mode. |
| LCD_D3 | 7 | Connect to Newhaven TFT `DB11` for 8-bit 8080-II mode. |
| LCD_D4 | 8 | Connect to Newhaven TFT `DB12` for 8-bit 8080-II mode. |
| LCD_D5 | 9 | Connect to Newhaven TFT `DB13` for 8-bit 8080-II mode. |
| LCD_D6 | 10 | Connect to Newhaven TFT `DB14` for 8-bit 8080-II mode. |
| LCD_D7 | 11 | Connect to Newhaven TFT `DB15` for 8-bit 8080-II mode. |
| LCD_WR | 12 | Write strobe. |
| LCD_DC | 13 | Data/command. |
| LCD_CS | 14 | Chip select. |
| DISP_TOUCH_RST | 15 | TFT `/RES`; also route to CTP `/RESET` unless final timing test requires separation. |
| LCD_BL_PWM | 16 | Backlight driver dimming input, not direct LED drive. |
| LCD_RD/RDX | Tie inactive | Pull TFT pin 13 `RDX` high with 10 k ohm if readback is unused. |
| IM0 | Strap high | 8-bit 8080-II mode. |
| IM1 | Strap low | 8-bit 8080-II mode. |
| IM2 | Strap low | 8-bit 8080-II mode. |
| TFT DB0-DB7 | - | Leave TFT pins 14-21 unused in 8-bit mode. |
| TFT DB8-DB15 | 4-11 | Connect TFT pins 22-29 to `LCD_D0`-`LCD_D7`. |
| TFT SDO/SDA/TE | - | Not used for 8-bit parallel; optional test pads only. |
| TFT LED-A | - | Backlight anode to `SYS_5V` / backlight supply. |
| TFT LED-K1..K4 | - | Backlight cathodes tied together to STCS1A `DRAIN`; STCS1A `FB` goes only to the sense resistor. |
| 3V3 | - | Display logic. |
| GND | - | Return. |

### J4 - Touch FFC

Exact pinout follows the selected Newhaven touch panel/datasheet.

Connector:

- 6-pin, 1.0 mm pitch FFC/ZIF.
- Recommended datasheet connector: Molex `52271-0679` or similar.
- The Newhaven `NHD-CTP6` breakout is for prototyping only.
- Touch is I2C; the TFT graphics interface is separate.

| Signal | ESP32 GPIO | Notes |
|---|---:|---|
| I2C_SCL | 17 | Shared I2C bus. |
| I2C_SDA | 18 | Shared I2C bus. |
| TOUCH_INT | 21 | Touch interrupt. |
| TOUCH_RST | 15 | Controlled reset shared with TFT reset; do not tie directly to VCC. |
| 3V3 | - | Touch logic. |
| GND | - | Return. |

### J5 - Front-Panel HMI Board

Selected connector family: JST GH, 1.25 mm pitch, locking wire-to-board.

Use a 14-position connector for the main-to-front-panel harness.

Recommended parts:

| Use | Part | Notes |
|---|---|---|
| Main PCB header, top-entry | `BM14B-GHS-TBT(LF)(SN)` | Use if the cable exits vertically from the PCB. |
| Main PCB header, side-entry alternate | `SM14B-GHS-TB(LF)(SN)` | Use if the cable exits parallel to the PCB. |
| Front-panel PCB header, matching style | `BM14B-GHS-TBT(LF)(SN)` or `SM14B-GHS-TB(LF)(SN)` | Choose top/side entry based on mechanical layout. |
| Cable housing | `GHR-14V-S` | One housing at each cable end if using headers on both PCBs. |
| Crimp contacts | `SSHL-002T-P0.2` | One crimp per wire end. Supports AWG 26-30. |

Important Altium/library note:

- `BMxxB-GHS...` and `SMxxB-GHS...` are PCB-mounted headers.
- `GHR-xxV-S` is the free-hanging cable housing, not the PCB footprint.
- In the Altium search screenshot, `BM03B-GHS-TBT...` is the right series but only 3 positions. For this harness use the 14-position version.

If the mechanical design needs an extra spare or keying trick later, a 15-position JST GH version is the largest standard GH option in this family. The current signal list fits cleanly in 14 positions.

| Pin | Signal | Notes |
|---:|---|---|
| 1 | VLED_5V | 5 V LED common-anode supply for NKK RGB buttons. |
| 2 | VLED_5V | Duplicate for current/return symmetry. |
| 3 | SYS_3V3 | Logic supply for PCAL9555A and TLC5947. |
| 4 | GND | Return. |
| 5 | GND | Return. |
| 6 | I2C_SCL | Shared bus from GPIO17. |
| 7 | I2C_SDA | Shared bus from GPIO18. |
| 8 | HMI_INT | GPIO47, open-drain interrupt from PCAL9555A. |
| 9 | LED_SIN_HMI | GPIO39 to TLC5947 through 33 ohm series resistor on main PCB. |
| 10 | LED_SCLK_HMI | GPIO40 to TLC5947 through 33 ohm series resistor on main PCB. |
| 11 | LED_LAT_HMI | GPIO41 to TLC5947 through 33 ohm series resistor on main PCB. |
| 12 | LED_BLANK_HMI | GPIO42 to TLC5947 through 33 ohm series resistor on main PCB. |
| 13 | BTN_MULTI_WAKE | GPIO48 direct wake line. |
| 14 | HMI_RESERVED | Future HMI signal or no-connect. |

Front-panel PCB devices:

- 8x NKK KP01 RGB pushbuttons.
- 1x PCAL9555A I2C GPIO expander.
- 1x TLC5947 RGB LED driver.
- LED current-set resistor.
- I2C pull-up strategy coordinated with main PCB and touch controller.
- Main PCB provides 10 k pull-ups for `HMI_INT` and `BTN_MULTI_WAKE`.
- Local decoupling.
- Test pads for I2C, LED serial signals, 3V3, VLED, and GND.

### J6 - Buzzer

Preferred v1 buzzer is mounted directly on the main PCB:

- TDK `PS1240P02BT`, passive piezo transducer.
- `BUZZER_PWM` drives the piezo through a 100 ohm series resistor.
- Add 1 Mohm bleed resistor across the piezo.

If the buzzer is not mounted on the main PCB, use a 2-pin connector:

| Pin | Signal | Notes |
|---:|---|---|
| 1 | BUZZER_DRIVE | From `BUZZER_PWM` through 100 ohm series resistor. |
| 2 | GND | Return. |

No MOSFET or flyback diode is needed for the selected passive piezo. If a louder active magnetic buzzer is selected later, use a low-side MOSFET driver instead.

### J7 - Debug / Test Pads

Expose at minimum:

| Signal | Notes |
|---|---|
| 3V3 | Probe point. |
| SYS_5V | Probe point. |
| GND | Multiple probe points. |
| EN | Reset/debug. |
| GPIO0 / BOOT | Boot mode. |
| USB_DN / USB_DP | Optional test pads near USB routing if layout allows. |
| U0TXD / U0RXD | Optional test pads only; rely on USB Serial/JTAG for normal logs/programming. |
| I2C_SCL / I2C_SDA | Debug bus. |
| SCAN_TX / SCAN_RX | Scanner serial debug. |

## 5. Front-Panel Expander Input Allocation

PCAL9555A input allocation:

| Expander Pin | Signal | Notes |
|---|---|---|
| P0_0 | BTN_USER_1 | Active low. |
| P0_1 | BTN_USER_2 | Active low. |
| P0_2 | BTN_USER_3 | Active low. |
| P0_3 | BTN_USER_4 | Active low. |
| P0_4 | BTN_DIRECTION | Active low. |
| P0_5 | BTN_QTY_PLUS | Active low. |
| P0_6 | BTN_QTY_MINUS | Active low. |
| P0_7 | BTN_MULTI | Active low; same physical switch also pulls BTN_MULTI_WAKE low. |
| P1_0 | FP_RESERVED_0 | Spare input/test. |
| P1_1 | FP_RESERVED_1 | Spare input/test. |
| P1_2 | FP_RESERVED_2 | Spare input/test. |
| P1_3 | FP_RESERVED_3 | Spare input/test. |
| P1_4 | FP_RESERVED_4 | Spare input/test. |
| P1_5 | FP_RESERVED_5 | Spare input/test. |
| P1_6 | FP_RESERVED_6 | Spare input/test. |
| P1_7 | FP_RESERVED_7 | Spare input/test. |

The spare expander pins can later support lid sensor, enclosure tamper, rotary encoder experiment, service button, or front-panel revision detection.

## 6. LED Channel Allocation

TLC5947 channel allocation:

| Channel | LED |
|---:|---|
| 0 | USER_1_R |
| 1 | USER_1_G |
| 2 | USER_1_B |
| 3 | USER_2_R |
| 4 | USER_2_G |
| 5 | USER_2_B |
| 6 | USER_3_R |
| 7 | USER_3_G |
| 8 | USER_3_B |
| 9 | USER_4_R |
| 10 | USER_4_G |
| 11 | USER_4_B |
| 12 | DIRECTION_R |
| 13 | DIRECTION_G |
| 14 | DIRECTION_B |
| 15 | QTY_PLUS_R |
| 16 | QTY_PLUS_G |
| 17 | QTY_PLUS_B |
| 18 | QTY_MINUS_R |
| 19 | QTY_MINUS_G |
| 20 | QTY_MINUS_B |
| 21 | MULTI_R |
| 22 | MULTI_G |
| 23 | MULTI_B |

Verified topology:

- NKK KPRGB LED wiring is common-anode style with separate red/green/blue cathodes.
- TLC5947 current-sink outputs connect to the color cathodes.
- Use 5 V `VLED` for LED common-anode supply.

## 7. Risks And Watch Items

| Item | Risk | Mitigation |
|---|---|---|
| No spare ESP32 GPIO | Late feature additions may be painful. | Use front-panel expander spares; avoid adding direct MCU GPIO needs. |
| GPIO43/44 reuse | Default UART0 pins can be active during boot. | Avoid using TXD0/GPIO43 for power enables; use USB Serial/JTAG on GPIO19/20 for logs/programming. |
| Scanner UART voltage unknown | ESP32 GPIO is not 5 V tolerant. | Include level-shifter/protection footprint. |
| Shared I2C bus length | Touch + HMI board share I2C. | Keep harness short, use sane pull-ups, test at 100 kHz first. |
| Touch reset pin | Touch reset should not be tied directly to VCC. | Share `DISP_TOUCH_RST` with TFT reset unless testing requires a separate GPIO. |
| Strapping pins | Accidental loading can break boot. | Keep GPIO0/3/45/46 away from normal HMI and external connectors. |

## 8. Next Checks Before Schematic Lock

1. Transfer exact Newhaven TFT and touch FFC pinouts into Altium symbols.
2. Confirm the display supports 8-bit I80 with `LCD_RD` tied inactive.
3. Bench-measure Waveshare scanner UART voltage.
4. Confirm KP01 footprint and RGB LED pin numbering against the exact package drawing.
5. Decide JST-GH vs JST-PH vs FFC for the front-panel connector.
6. Decide whether `SCAN_AUX_SPARE` becomes a real spare or supports a future scanner variant.

## 9. Sources

- ESP32-S3-WROOM-1/WROOM-1U datasheet: https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- ESP-IDF GPIO guide: https://docs.espressif.com/projects/esp-idf/en/v5.3.3/esp32s3/api-reference/peripherals/gpio.html
- ESP-IDF I80 LCD guide: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/i80_lcd.html
- NXP PCAL9555A: https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/low-voltage-16-bit-ic-bus-gpio-with-agile-i-o-interrupt-and-weak-pull-up:PCAL9555A
- TI TLC5947: https://www.ti.com/product/TLC5947
