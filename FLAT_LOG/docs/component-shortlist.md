# Component Shortlist

This document records candidate components and provisional decisions for the fridge inventory device. The goal is a polished one-off unit with industrial design habits, not a cost-minimized product.

## 1. Baseline Decisions

| Area | Baseline | Status |
|---|---|---|
| MCU | ESP32-S3-WROOM-1U-N16R8 | Preferred |
| Antenna | Hidden internal 2.4 GHz FPC/adhesive antenna via U.FL/I-PEX | Preferred |
| Display | Newhaven-style 2.8 inch IPS TFT with capacitive touch | Preferred |
| Display bus | 8-bit I80/8080 parallel using Newhaven `DB8-DB15` + I2C touch | Preferred |
| UI | Physical buttons primary, touch secondary | Decided for v1 |
| Scanner | Waveshare Barcode Scanner Module, low-cost decoded 1D/2D UART/USB module | Preferred |
| Power | USB-C only, hybrid rear power switch plus front sleep/wake | Preferred |
| 3.3 V regulator | AP63203-class 2 A synchronous buck | Preferred |
| Input protection | TPS2595-class eFuse | Preferred |
| Scanner power switch | TPS22919-class load switch | Preferred |
| Momentary buttons | 8x NKK KP01 RGB illuminated pushbuttons, preferred DigiKey part `KP0115ANBKG03RGBP-3SJB` | Preferred |
| LED driver | TI TLC5947 24-channel constant-current PWM driver, exactly covers 8 RGB buttons | Preferred |
| Button GPIO expander | NXP PCAL9555A 16-bit I2C GPIO expander on front-panel PCB | Preferred |
| IN/OUT control | Momentary NKK KP01 direction button, default IN, lit/toggled OUT | Preferred |
| Main power control | NKK `UB216KKG015C`, UB2 latching illuminated red pushbutton controlling eFuse enable | Locked |
| Hidden service switch | E-Switch EG1218 slide switch, optional | Fallback / service-only |

## 2. MCU

### 2.1 Preferred MCU Module

**ESP32-S3-WROOM-1U-N16R8**

Reasons:

- ESP32-S3 class module has enough GPIO for display, scanner, buttons, switches, LEDs, buzzer, and debug.
- Native USB supports a clean programming/debug path.
- 16 MB flash and 8 MB PSRAM give comfortable headroom for LVGL, OTA, TLS, event queue, and UI assets.
- The `1U` module variant uses an external antenna connector, allowing a hidden internal antenna to be placed optimally in the enclosure.
- Espressif provides module footprints and models suitable for CAD integration.

Design notes:

- Treat the antenna as a mechanical component from the start.
- Keep enough margin on the 3.3 V rail for Wi-Fi current peaks.
- Reserve pins carefully around USB, boot strapping, flash/PSRAM constraints, and debug.

Sources:

- Espressif module page: https://www.espressif.com/en/products/modules/esp32-s3-wroom-1u
- Espressif datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf

## 3. Antenna

### 3.1 Preferred Antenna Class

Hidden internal 2.4 GHz FPC/adhesive antenna with U.FL/I-PEX-compatible connector.

Requirements:

- 2.4 GHz Wi-Fi compatible.
- 50 ohm nominal impedance.
- Gain compatible with module certification constraints.
- Mechanically mountable inside the plastic enclosure.
- Coax length short enough to avoid unnecessary loss, but long enough to place the antenna well.

Placement preference:

- High and rearward in the enclosure.
- Away from USB cable routing.
- Away from the display FFC and scanner body.
- Away from large ground pours, metal fasteners, metal-filled filament, carbon-filled filament, and the fridge body.

Validation:

- Add firmware diagnostics for RSSI and sync state.
- Test with final enclosure in the actual kitchen location before closing the antenna decision.

## 4. Display

### 4.1 Preferred Display Class

Newhaven-style 2.8 inch IPS TFT with capacitive touch.

Representative candidate:

**Newhaven NHD-2.8-240320AF-CSXP-FCTP**

Not yet final, but matches the desired class:

- 2.8 inch diagonal.
- 240 x 320 resolution.
- IPS.
- High brightness.
- Capacitive touch with cover glass.
- 3.3 V supply.
- ST7789VI display controller.
- FT5426 capacitive touch controller.
- SPI or 8/16-bit parallel display interface.
- I2C touch interface.
- FFC/ZIF style connection.

Recommendation:

- Keep this as the baseline display class.
- Prefer SPI for first firmware simplicity unless UI performance testing pushes us to parallel.
- If selecting the exact Newhaven part, create an Altium component directly from the official datasheet and FFC pinout.

Source:

- Newhaven product page: https://newhavendisplay.com/2-8-inch-ips-capacitive-tft-display/

### 4.2 Alternate Display Class

Riverdi-style intelligent EVE/BT817 display.

Why it remains interesting:

- Strong industrial HMI module feel.
- Onboard graphics controller.
- Good touch/display integration.
- SPI/QSPI host interface.

Why it is not v1 baseline:

- Larger and more expensive.
- More opinionated graphics programming model.
- Less direct LVGL/framebuffer-style freedom.
- Better fit for a future touch-centric v2 with fewer physical buttons.

Source:

- Riverdi 3.5 inch EVE4 capacitive display: https://riverdi.com/product/eve4-intelligent-display-rvt35hhbnwc00-3-5-inch-projected-capacitive-touch-panel-air-bonding-uxtouch/

## 5. Barcode Scanner

### 5.1 Scanner Requirements

The scanner should be a decoded 1D/2D scan engine or module.

Required:

- Unit cost under 120 USD.
- Reads common grocery 1D barcodes, especially EAN-13 and UPC-A.
- Reads 2D codes such as QR codes for future flexibility.
- UART or TTL serial interface strongly preferred.
- USB support is useful for development but not required for final integration.
- Integrated illumination and aiming.
- Trigger input or command-controlled scanning.
- Reasonable documentation for configuration.

Preferred:

- Cheaper is better if scan quality and integration remain acceptable.
- 3.3 V logic.
- 3.3 V or 5 V power with known peak current.
- Common connector or included cable.
- Published pinout and UART/USB configuration manual.
- Direct serial output of decoded barcode data with configurable suffix.
- Configurable suffix/prefix behavior.
- Ability to disable built-in beep if the product handles sound itself.

### 5.2 Scanner Selection Shift

Premium OEM scan engines are no longer the baseline. They are technically attractive, but they tend to create sourcing, connector, protocol, and documentation friction that is not justified for this product.

The scanner is important, but it is not the heart of the project. The product value is the complete appliance: enclosure, UI, event model, backend, and reliable workflow. Therefore the best scanner is the one that scans grocery barcodes reliably and integrates cleanly.

New scanner baseline:

- Under 120 USD.
- UART/TTL serial output.
- USB available for debugging.
- 1D and 2D support.
- Easy to purchase as a one-off.
- Published integration docs.
- Not mechanically huge.

### 5.3 Selected Baseline - Waveshare Barcode Scanner Module

Position: selected baseline scanner for v1, pending bench validation.

Why it fits:

- Current listed price around 40 USD.
- 1D/2D barcode support.
- UART and USB interfaces.
- 5 V operation.
- Onboard illumination.
- Includes cable according to product listing.
- Published wiki/manual resources.
- Small, rectangular module shape is likely easier to mount behind a front/angled scan window.

Risks / checks:

- Uses micro USB on the module for USB development, not USB-C.
- UART logic level must be confirmed before direct ESP32 connection.
- Need to validate scan reliability on real grocery packaging.
- Need to confirm whether command trigger/presentation mode works well enough for the desired UX.
- The product-page connector looks simple, but exact mating connector/cable detail must be checked before schematic lock.

Source:

- Waveshare Barcode Scanner Module: https://www.waveshare.com/barcode-scanner-module.htm

### 5.4 Candidate B - DFRobot GM73

Position: very attractive low-cost candidate if availability is good.

Why it fits:

- Current listed price around 39 USD.
- USB and UART.
- Multiple scan modes including manual, continuous, sensing, and host mode.
- 5 V power.
- Low current according to listing.
- Strong ambient-light tolerance.
- Ships with USB cable and TTL adapter according to product listing.
- Recent product/version, so potentially better documentation and behavior than older GM65-class modules.

Risks / checks:

- DFRobot listing shows limited stock at time of research.
- Exact UART electrical level and command protocol should be verified in the manual.
- Need mechanical drawing and mounting strategy.
- Need to confirm whether documentation is stable enough for a custom PCB integration.

Source:

- DFRobot GM73: https://www.dfrobot.com/product-2601.html

### 5.5 Candidate C - DFRobot GM77

Position: stronger DFRobot module, still comfortably below budget.

Why it fits:

- Current listed price around 56 USD.
- USB and TTL-232.
- 1D/2D support.
- Auto-sensing behavior.
- Documented depth-of-field examples.
- Ships with USB adapter cable and TTL adapter cable according to product listing.

Risks / checks:

- Larger than some alternatives.
- 5 V operation means UART level must be checked.
- Slightly more expensive than GM73/Waveshare without necessarily being better for grocery use.

Source:

- DFRobot GM77: https://www.dfrobot.com/product-2480.html

### 5.6 Candidate D - DFRobot GM65

Position: known pragmatic candidate.

Why it fits:

- Current listed price around 50 USD.
- 1D/2D support.
- USB and UART.
- 5 V power.
- Moderate current.
- Existing hobby/community visibility.
- Good for firmware/backend prototyping and enclosure exploration.

Risks / checks:

- More maker-module style than OEM scan engine.
- Larger module board may constrain enclosure design.
- UART logic level must be checked before direct ESP32 connection.
- GM73/GM77 may be better current DFRobot options.

Source:

- DFRobot GM65 page: https://www.dfrobot.com/product-1996.html

### 5.7 Candidate E - SparkFun DE2120 Breakout

Position: easiest documented integration candidate, but not the cheapest.

Why it fits:

- Current listed price around 67 USD.
- Easy breakout board for early testing.
- USB-C and TTL serial.
- Trigger/status access.
- Good tutorials and schematics.
- Standard 0.1 inch header for power, serial UART, trigger, and status according to SparkFun's hookup guide.
- Arduino library, Python package, settings manual, schematic, and hardware files available.
- Strong choice if "easy integration" matters more than the last 25 USD.

Risks / checks:

- Breakout board may be mechanically awkward in the final enclosure.
- Underlying module sourcing should be checked if using the bare engine.
- SparkFun marks it as an experimental/SparkX-style product in some documentation, so availability should be checked before relying on it.

Source:

- SparkFun SEN-18088 page: https://www.sparkfun.com/products/18088
- SparkFun hookup guide: https://learn.sparkfun.com/tutorials/2d-barcode-scanner-breakout-hookup-guide/introduction

### 5.8 Candidate F - DFRobot Gravity Ring 2D Scanner

Position: cheap and very easy electrically, but mechanical fit is less obvious.

Why it fits:

- Current listed price around 40 USD.
- Supports 3.3 V and 5 V.
- UART and I2C.
- Very low current compared with many rectangular modules.
- Four-pin Gravity-style interface is simple.
- Official wiki provides pinout and example code.

Risks / checks:

- Round form factor may be better for access-control style QR scanning than grocery barcode scanning.
- Need real EAN-13 grocery barcode tests before selecting it.
- Mechanical mounting and scan window design may be less natural for a countertop product.

Source:

- DFRobot Gravity Ring Scanner: https://www.dfrobot.com/product-2485.html
- DFRobot wiki: https://wiki.dfrobot.com/SKU_SEN0486_Gravity_Ring_2D_QR_Code_Scanner

## 6. Scanner Recommendation

Recommended path:

1. Use the **Waveshare Barcode Scanner Module** as the v1 baseline.
2. Buy or evaluate a SparkFun DE2120 Breakout only if the Waveshare UART protocol, documentation, or scanning behavior becomes a blocker.
3. Keep DFRobot GM73 as the closest low-cost alternate.
4. Prefer UART integration to USB-host integration.
5. Use the Waveshare-supplied cable/connector style where practical, but route the main PCB so a later scanner change does not require a full architecture change.
6. Keep the main PCB scanner connector electrically flexible:
   - 5 V scanner power rail, switchable.
   - 3.3 V rail available if final engine needs it.
   - UART TX/RX with optional level shifting.
   - Trigger input.
   - Good-read/status input.
   - Optional USB D+/D- test path or pads.
7. Do not lock the enclosure scanner window until field of view, working distance, and mounting geometry are tested with real food packaging.

Current preference for final unit: **Waveshare Barcode Scanner Module**, pending UART level/protocol and mechanical validation.

Most conservative integration choice: **SparkFun DE2120 Breakout**.

## 6.1 Current Scanner Ranking

| Rank | Candidate | Approx. Price | Why |
|---:|---|---:|---|
| 1 | Waveshare Barcode Scanner Module | 40 USD | Selected baseline. Cheap, UART/USB, common-looking cable, compact, good enough baseline. |
| 2 | DFRobot GM73 | 39 USD | Cheap, UART/USB, multiple scan modes, attractive specs, but stock/docs need checking. |
| 3 | SparkFun DE2120 Breakout | 67 USD | Best documentation/integration, USB-C, standard header, but less final-product elegant. |
| 4 | DFRobot GM77 | 56 USD | Strong specs, UART/USB, likely usable, maybe larger than needed. |
| 5 | DFRobot GM65 | 50 USD | Known workable module, but older/less compelling than GM73/GM77. |
| 6 | DFRobot Gravity Ring | 40 USD | Very easy electrical interface, but round mechanical concept needs grocery scanning tests. |

## 7. Immediate Open Questions

| ID | Question | Why It Matters |
|---|---|---|
| CQ-001 | Can the Waveshare scanner be sourced conveniently to Switzerland/EU? | Determines first test hardware. |
| CQ-002 | Is the exact Newhaven display available from a convenient distributor? | Determines whether we lock the FFC and mechanical cutout. |
| CQ-003 | Do we want display over SPI or parallel? | Affects ESP32 pinout, connector, and UI performance. |
| CQ-004 | Should scanner be always-on, triggered by command, or awakened by object/presentation mode? | Affects UX, power, and enclosure opening. |
| CQ-005 | Should barcode scan window be front-facing, top-facing, or angled? | Major enclosure decision. |
| CQ-006 | Are scanner UART signals 3.3 V tolerant, 5 V TTL, or RS232-level? | Determines level shifting/protection. |
| CQ-007 | Does selected scanner support command-triggered scanning and configurable suffix? | Determines firmware parser and UX. |
