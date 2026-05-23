# Power And I/O Architecture

This document defines the v1 electrical architecture for USB-C power, switching, display interface, scanner power, and front-panel controls.

## 1. Design Goals

- USB-C powered only.
- No USB-PD requirement for v1.
- Professional input protection and current limiting.
- Physical rear/side power switch.
- Front multifunction button for wake/sleep/shared/settings behavior.
- 5 V rail available for scanner and display backlight.
- 3.3 V rail for ESP32-S3 module, display logic, touch controller, and front-panel logic.
- Display bus fast enough for a polished UI.
- User controls remain physical and reliable.
- Last scanned item must survive abrupt power removal.

## 2. Power Tree

```text
USB-C receptacle
   |
   |-- CC1/CC2 Rd resistors
   |-- USB D+/D- ESD protection
   |-- VBUS protection
   |
USB_VBUS_5V
   |
eFuse / protected power switch
   |   ^
   |   |
   | rear physical ON/OFF switch drives enable
   |
SYS_5V
   |---------------------> scanner load switch -> SCANNER_5V
   |---------------------> display backlight driver / backlight rail
   |
3.3 V buck regulator
   |
SYS_3V3
   |---------------------> ESP32-S3-WROOM-1U
   |---------------------> display logic
   |---------------------> capacitive touch controller
   |---------------------> buttons / LEDs / level shifters
```

## 3. USB-C Input

V1 should use USB-C as a simple 5 V sink.

Required:

- USB-C receptacle.
- CC1 and CC2 sink pulldown resistors.
- D+/D- routed to ESP32-S3 native USB for programming/logging.
- USB D+/D- ESD protection near the connector.
- VBUS protection and current limiting.
- Shield grounding strategy decided during PCB layout.

No USB-PD controller is required for v1 because the device should fit inside a modest 5 V current budget.

Target current budget:

| Load | Rail | Estimated Current |
|---|---|---:|
| ESP32-S3 Wi-Fi peaks | 3.3 V | 300-500 mA peak |
| Display logic + touch | 3.3 V | 20-60 mA |
| Display backlight | 5 V / LED driver | 100-200 mA class |
| Waveshare scanner | 5 V | 210 mA scanning, according to listing |
| LEDs / buzzer / margin | mixed | 100-200 mA |

Design target: stay under about 900 mA steady input current where practical, with enough transient margin that Wi-Fi, scanner illumination, and display backlight can overlap without brownout.

## 4. Input Protection And Switching

### 4.1 Preferred Input Protection

Use an eFuse/load-switch-style protected input path rather than only a resettable fuse.

Preferred candidate class:

- TI TPS2595-class eFuse.

Why:

- Adjustable current limit.
- Overvoltage protection.
- Soft-start/inrush control.
- Fault output.
- Thermal shutdown.
- Cleaner behavior than a bare polyfuse.

Open choice:

- Exact eFuse variant and current limit.
- Whether the rear power switch disconnects VBUS physically or drives the eFuse enable pin.

### 4.2 Preferred Power Switch Behavior

Use the rear/side power switch to control the protected system rail enable.

Behavior:

- Switch OFF disables SYS_5V and SYS_3V3.
- Switch ON enables SYS_5V and the 3.3 V regulator.
- This counts as the physical on/off switch for the product.
- It does not need to be a high-current mechanical switch if it controls the eFuse EN pin.

Important firmware implication:

- Because rear power-off may be abrupt, the active scanned item shall be journaled immediately after scan and after every quantity update.

### 4.3 Front Multifunction Button

The front multifunction button is not the hard power switch.

It is an MCU input used for:

- Wake from sleep.
- Return to Shared scope.
- Commit active item and return to Shared scope.
- Long-press sleep.
- Long-press settings/provisioning from wake, if desired.

This button should connect to a wake-capable ESP32-S3 GPIO, not only through an I/O expander.

## 5. 3.3 V Regulator

Preferred regulator class:

- 2 A synchronous buck regulator.
- Input compatible with USB 5 V.
- Good transient response.
- Low external component count.
- Reasonable EMI behavior.

Candidate:

- Diodes Inc. AP63203 fixed 3.3 V, 2 A buck.

Why it fits:

- 3.8 V to 32 V input range.
- 2 A output.
- Fixed 3.3 V option.
- Integrated compensation.
- Frequency spread spectrum for EMI reduction.
- Small TSOT26 package.

Design notes:

- Place buck close to power entry and 3.3 V loads.
- Keep hot loop compact.
- Follow datasheet layout guidance.
- Provide test points for SYS_5V, SYS_3V3, EN, and GND.
- Add enough bulk capacitance near the ESP32-S3 module.

## 6. Display Interface

Selected display class:

- Newhaven NHD-2.8-240320AF-CSXP-FCTP or equivalent.

Preferred bus for v1:

- 8-bit I80/8080 parallel display bus.
- I2C capacitive touch.

Rationale:

- Better UI update performance than SPI.
- Much lower pin cost than 16-bit parallel.
- Supported by ESP32-S3 `esp_lcd`.
- Good middle ground between simplicity and polished UI.

Display electrical blocks:

- 40-pin 0.5 mm FFC/ZIF connector for TFT.
- 6-pin 1.0 mm FFC/ZIF connector for capacitive touch.
- Backlight driver or controlled current path.
- Backlight PWM/dimming signal from ESP32-S3.
- Display reset GPIO.
- Optional TE signal if useful for tearing-aware updates.

Open display questions:

- Transfer the verified Newhaven revision/pinout into the Altium symbols.
- Route logical `LCD_D0-D7` to Newhaven TFT `DB8-DB15`.
- Strap `IM0=1`, `IM1=0`, `IM2=0` for 8-bit 8080-II mode.

## 7. Display Backlight

The Newhaven display backlight should not be treated as a random LED on a GPIO.

Preferred:

- Dedicated dimmable LED/backlight driver or controlled current sink according to the exact display datasheet.

Verified display backlight interface:

- `LED-A` is the backlight anode.
- `LED-K1` through `LED-K4` are backlight cathodes.
- Backlight current is 160 mA class at about 3.1 V.

Preferred implementation direction:

- Use a current-regulated backlight drive from the 5 V rail.
- A boost LED driver is not automatically required because the LED voltage is below the 5 V input rail.
- A controlled current sink or small buck/linear LED-driver topology is a better first-pass fit than assuming a boost converter.

Open item:

- Select the exact backlight current-control IC/circuit after schematic-level review.

## 8. Scanner Interface

Selected baseline:

- Waveshare Barcode Scanner Module.

Power:

- Powered from SYS_5V through a controllable scanner load switch.
- Scanner rail name: SCANNER_5V.

Candidate scanner load switch:

- TI TPS22919-class protected load switch.

Why:

- 1.5 A rating is far above scanner need.
- Controlled rise time helps inrush.
- Short-circuit and thermal protection.
- Quick output discharge option.
- MCU GPIO can power-cycle scanner if it locks up.

Signals:

| Signal | Direction | Notes |
|---|---|---|
| SCAN_TX | Scanner to ESP32 | Decoded barcode UART data. Level shift if scanner TX is 5 V. |
| SCAN_RX | ESP32 to scanner | Commands/configuration. Level shift if scanner input expects 5 V. |
| SCAN_AUX_SPARE | ESP32 to scanner / spare | Baseline Waveshare 4-pin cable does not expose a hardware trigger. Keep as future/prototype spare. |
| SCAN_GOOD | Scanner to ESP32 | Optional status/good-read line if module exposes it. |
| SCANNER_PWR_EN | ESP32 to load switch | Allows sleep and recovery power-cycle. |

Level shifting:

- ESP32-S3 GPIO is not 5 V tolerant.
- Waveshare documents 5 V module power and TTL/UART wiring, but does not explicitly state the UART high-level voltage.
- Include a dual-supply level translator such as SN74LVC2T45/74LVC2T45 class, or equivalent unidirectional level-shift/protection circuit, by default.
- If scanner UART is bench-confirmed 3.3 V logic, the level-shifter footprint can be bypassed or simplified in assembly.

## 9. Front Panel Controls

### 9.1 Required Controls

- User 1 button.
- User 2 button.
- User 3 button.
- User 4 button.
- Direction IN/OUT button.
- Quantity + button.
- Quantity - button.
- Multifunction button.

### 9.2 Recommended Topology

Selected momentary button baseline:

- 8x NKK KP01 RGB illuminated pushbuttons.
- Preferred DigiKey part: `KP0115ANBKG03RGBP-3SJB`.
- Use for all user, direction, quantity, and multifunction buttons.
- Prefer click/tactile versions with diffused square caps.
- The `KP0115ANBKG03RGBP-3SJCF11` variant is electrically similar but has an `ON/OFF` marking, so it should only be considered for the multifunction button if that label is desired.

Selected IN/OUT direction control baseline:

- Momentary NKK KP01 illuminated pushbutton.
- Direction defaults to IN on wake.
- Button toggles OUT mode.
- Button illumination indicates OUT mode.

Selected rear power switch baseline:

- E-Switch EG1218 SPDT slide switch controlling eFuse/system enable.

Use a front-panel I2C GPIO expander for the normal button contacts. The multifunction button also has a direct wake-capable ESP32-S3 GPIO connection.

For button sensing, two options were considered:

| Option | Pros | Cons |
|---|---|---|
| Direct GPIO | Simple, deterministic, no extra IC | More harness pins and MCU GPIOs |
| I2C GPIO expander | Fewer harness pins, frees MCU GPIO for display, interrupt line can report button changes | Extra IC and firmware dependency |

Current preference:

- PCAL9555A-class I2C GPIO expander on the front-panel PCB for all eight button inputs.
- Multifunction button also wired to a wake-capable MCU GPIO in parallel with its expander input.
- Expander interrupt wired to a direct MCU GPIO.
- User-visible button LEDs driven by a dedicated LED driver on the front-panel PCB.

### 9.3 User Indication

Preferred v1 approach:

- Each momentary button has integrated RGB illumination via the NKK KP01 family.
- Active user button is bright in that user's assigned color.
- Shared scope is indicated primarily on display, optionally with a neutral status LED.
- Multifunction button can carry shared/sleep/provisioning/recovery status.

LED implementation options:

- Baseline: TI TLC5947 24-channel constant-current PWM LED driver.
- Eight RGB pushbuttons require exactly 24 LED channels.
- Avoid addressable RGB LEDs for the main HMI unless the mechanical plan changes.

Open item:

- Verify exact NKK KP01 RGB LED common terminal and pinout before locking the TLC5947 wiring.

## 10. Buzzer / Audio Feedback

Use a small piezo buzzer or magnetic buzzer driven by a transistor/MOSFET.

Feedback patterns:

- Short tick: scan accepted.
- Double tick: event queued/offline.
- Low/error tone: scan failed or no matching item on OUT.
- Optional mute setting in firmware.

The scanner module's own beep should be disabled if possible, so the device has consistent sound design.

## 11. Persistent Active Item Journal

The no-confirm UX creates a special reliability requirement.

Problem:

- A scan creates an active item.
- Quantity may be changed during a short editing window.
- The final event normally commits on next scan or timeout.
- Rear power-off can happen before timeout.

Solution:

- Immediately write an active-item journal record after every scan.
- Update the journal when +1/-1 changes quantity.
- Update or commit the journal when owner/direction changes.
- Clear the journal only after the event is safely committed to the local event queue.

Boot recovery options:

| Option | Behavior | Notes |
|---|---|---|
| Auto-commit | Commit recovered active item on boot | Simple, may surprise user if last scan was accidental |
| Ask on display | Show recovered item and ask keep/discard | Best UX, uses touch/buttons |
| Discard with log | Drop recovered item and show warning | Avoids accidental inventory changes, less reliable |

Current preference:

- Ask on display when a journal exists after reboot:
  - Keep/commit item.
  - Discard item.
  - Edit quantity if needed.

## 12. Schematic Sheet Plan

Recommended Altium schematic sheets:

1. `00_System_Block`
2. `01_USB_C_Input_Protection`
3. `02_5V_Power_Switching`
4. `03_3V3_Buck_Regulator`
5. `04_ESP32S3_Module`
6. `05_Display_Touch_Backlight`
7. `06_Scanner_Interface`
8. `07_Front_Panel_IO`
9. `08_Buzzer_Status_LED`
10. `09_Debug_Test_Points`

## 13. Open Decisions

| ID | Decision | Current Direction |
|---|---|---|
| PWR-001 | Exact eFuse | TPS2595-class, current limit TBD |
| PWR-002 | Exact 3.3 V buck | AP63203-class fixed 3.3 V, 2 A |
| PWR-003 | Backlight driver topology | Dedicated current control, exact circuit TBD after display datasheet check |
| PWR-004 | Scanner level shifting | Include footprint/provision until Waveshare UART level is confirmed |
| IO-001 | Button inputs | PCAL9555A I2C expander, plus direct multifunction wake line |
| IO-002 | User button illumination | NKK RGB buttons driven by TLC5947 |
| DISP-001 | Display bus | 8-bit I80/8080 parallel using Newhaven `DB8-DB15` |

## 14. Sources

- TI TPS2595 eFuse: https://www.ti.com/product/TPS2595
- Diodes Inc. AP63203 buck regulator: https://www.diodes.com/part/view/AP63203
- ST USBLC6-2 USB ESD protection: https://www.st.com/en/protections-and-emi-filters/usblc6-2.html
- Newhaven 2.8 inch IPS capacitive TFT: https://newhavendisplay.com/2-8-inch-ips-capacitive-tft-display/
- ESP-IDF I80 LCD documentation: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/i80_lcd.html
- TI TPS22919 load switch: https://www.ti.com/product/TPS22919
- NXP PCA9555 I/O expander: https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/16-bit-ic-bus-and-smbus-i-o-port-with-interrupt:PCA9555
- Nexperia 74LVC2T45 level translator: https://www.nexperia.com/product/74LVC2T45GN
