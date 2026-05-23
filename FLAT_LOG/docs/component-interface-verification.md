# Component Interface Verification

This document records what has been verified from datasheets/manuals and what still needs bench validation with real parts.

## 1. Summary

| Component | Status | Main Result |
|---|---|---|
| Newhaven `NHD-2.8-240320AF-CSXP-FCTP` | Datasheet verified | 8-bit I80 is supported, but it uses TFT `DB8-DB15`, not `DB0-DB7`. |
| Waveshare `Barcode Scanner Module` SKU 14810 | Manual verified, bench still required | 5 V module, UART/USB, 4-pin PH2.0 cable, UART default 9600 8N1 after configuration. UART logic voltage not explicitly specified. |
| NKK `KP0115ANBKG03RGBP-3SJB` | Distributor + datasheet info verified | SPST-NO Off-Mom RGB pushbutton. RGB LED is common-anode style, so TLC5947 current-sink driver is the right topology. |

## 2. Newhaven Display

Selected display:

- `NHD-2.8-240320AF-CSXP-FCTP`

Connector reality:

- The display has two separate FFC interfaces:
  - TFT graphics FFC: 40-pin, 0.5 mm pitch.
  - Capacitive touch FFC: 6-pin, 1.0 mm pitch.
- The capacitive-touch interface is I2C.
- The TFT graphics interface is not I2C. It is SPI or 8/16-bit 8080-II parallel.
- Newhaven's breakout boards are useful for prototyping, but they are not required for the final custom PCB.

Verified facts:

- TFT controller: ST7789VI.
- Touch controller: FT5426.
- TFT interface: 8/16-bit parallel and 3/4-wire SPI.
- Touch interface: I2C.
- TFT connector: 40-pin, 0.5 mm FFC, recommended Molex `54132-4062`.
- Touch connector: 6-pin, 1.0 mm FFC, recommended Molex `52271-0679`.
- TFT supply: 3.3 V.
- Touch supply: 3.3 V.
- Backlight: `LED-A` anode, `LED-K1` through `LED-K4` cathodes.
- Backlight current: 160 mA typ/max class at about 3.1 V.
- 8-bit 8080-II mode uses `DB8-DB15`, not `DB0-DB7`.
- Interface mode for 8-bit 8080-II: `IM0=1`, `IM1=0`, `IM2=0`.
- Touch `/RESET` should not simply be tied to VCC; the datasheet warns that data corruption can occur.

Design consequences:

- For the polished final PCB, place the 40-pin TFT FFC connector and 6-pin CTP FFC connector directly on the PCB that sits behind/near the display.
- Do not use Newhaven `NHD-FFC40`, `NHD-CTP6`, or the 2x20 IDC ribbon cable in the final enclosure unless a deliberate serviceable daughterboard architecture is chosen.
- The `NHD-FFC40` is a 40-pin 0.5 mm FFC to 2x20 2.54 mm breakout for prototyping.
- The `NHD-CTP6` is a 6-pin 1.0 mm FFC to 2.54 mm breakout for prototyping the capacitive-touch connection.
- The 2x20 IDC cable only makes sense with the 40-pin breakout board/prototyping path.
- Keep the ESP32 GPIO allocation for `LCD_D0` through `LCD_D7`, but connect those logical bits to TFT `DB8` through `DB15`.
- Tie TFT `RDX` inactive if display readback is not used.
- Route or strap `IM0/IM1/IM2` for 8-bit 8080-II mode.
- Drive TFT `/RES` and touch `/RESET` from a controlled reset net. Sharing one ESP32 reset GPIO is acceptable as the baseline.
- Treat the backlight as a real current-regulated load. Do not drive it directly from GPIO or through only a casual resistor.

## 3. Waveshare Barcode Scanner

Selected scanner:

- Waveshare `Barcode Scanner Module`, SKU 14810, Part No. `Barcode Scanner Module`

Verified facts:

- Product price class: about 40 USD.
- Operating voltage: 5 V.
- Operating current: 210 mA scanning, <=25 mA standby, 2 mA sleep according to product page.
- Interfaces: UART and USB.
- USB connector on module: micro USB.
- Included cable: PH2.0 4-pin.
- 4-pin UART/power naming from manual:
  - `VCC`: 5 V
  - `TX`: scanner transmit, connect to MCU RX
  - `RX`: scanner receive, connect to MCU TX
  - `GND`: ground
- Factory default output: manual scanning, USB PC output.
- UART output requires scanning the UART output configuration code.
- UART default after configuration: 9600 baud, 8 data bits, 1 stop bit.
- Terminator can be configured, including CR and CRLF.
- Real grocery-relevant EAN-13 is supported by factory settings.
- Manual gives EAN-13 scan distance as approximately 3 cm to 43 cm under stated indoor test conditions.
- If adding an enclosure window, Waveshare recommends a colorless, clean, smooth, close, non-skewed window.

Unverified / bench required:

- UART logic level is not explicitly stated as 3.3 V or 5 V TTL.
- Whether the module's UART `TX` high level is safe for ESP32-S3 input.
- Whether serial-command triggered scanning is reliable enough for our UX.
- Real scanning behavior through the chosen enclosure window.

Design consequences:

- Use a 5 V switchable scanner supply.
- Include a level-shifter/protection footprint on scanner UART by default.
- Treat hardware trigger/status pins as optional only; the selected Waveshare 4-pin connector does not expose them.
- Configure scanner to UART mode and CRLF terminator during setup.
- Test real grocery packaging before freezing scanner angle and window geometry.

## 4. NKK RGB Pushbutton

Selected switch:

- `KP0115ANBKG03RGBP-3SJB`

Verified facts:

- Series: KPRGB / KP RGB expansion.
- Circuit: SPST-NO.
- Function: Off-Momentary.
- Mounting: through-hole.
- Actuator: square button.
- Marking: no marking.
- Cap: clear with white filter/diffuser.
- Illumination: RGB LED.
- Nominal LED forward voltages listed by DigiKey: 2.0 V, 2.9 V, 2.9 V.
- Switch rating: 100 mA at 12 VDC.
- Mechanical/electrical life listed by DigiKey: 5,000,000 cycles.
- NKK KPRGB datasheet information shows a common-anode RGB LED arrangement with separate color cathodes.

Design consequences:

- TLC5947 remains the correct baseline LED driver because it is a constant-current sink driver.
- Use `VLED=5V` for the common anodes to give enough LED-driver headroom for green/blue.
- TLC5947 outputs connect to the individual red/green/blue cathodes.
- No separate LED series resistors are needed per channel if the TLC5947 current is set correctly.
- Button contacts go to the PCAL9555A input expander, with the multifunction contact also wired to the direct wake line.

Bench / ordering check:

- Before PCB fab, compare the final Altium footprint against the exact NKK package drawing for `KP0115ANBKG03RGBP-3SJB`.
- Verify cap height and spacing with a quick front-panel mechanical print or cardboard layout.

## 5. Required Design Updates

| Item | Update |
|---|---|
| TFT data mapping | Logical `LCD_D0-D7` shall connect to Newhaven `DB8-DB15`. |
| TFT mode straps | `IM0=1`, `IM1=0`, `IM2=0` for 8-bit 8080-II. |
| Touch reset | Use controlled reset, shared with TFT reset unless later testing says otherwise. |
| Backlight | Use current-regulated backlight drive; avoid the previous assumption that a boost LED driver is automatically required. |
| Scanner UART | Include level shifting/protection. Do not assume 3.3 V. |
| Scanner trigger | Treat as optional/not available on selected 4-pin Waveshare module. |
| HMI LEDs | Use TLC5947 sink topology with 5 V common-anode supply. |

## 6. Sources

- Newhaven display datasheet: https://newhavendisplay.com/content/specs/NHD-2.8-240320AF-CSXP-FCTP.pdf
- Newhaven ECN / transition notice: https://support.newhavendisplay.com/hc/en-us/articles/33514439173271-07-16-25-NHD-2-8-240320AF-CSXP-F
- Waveshare product page: https://www.waveshare.com/barcode-scanner-module.htm
- Waveshare wiki: https://www.waveshare.com/wiki/Barcode_Scanner_Module
- Waveshare quick start: https://files.waveshare.com/upload/3/35/Barcode_Scanner_Module_Quick_Start_EN.pdf
- Waveshare setting manual V2.1: https://files.waveshare.com/wiki/Barcode-Scanner-Module/Barcode_Scanner_Module_Setting_Manual_V2.1.pdf
- DigiKey NKK button page: https://www.digikey.com/en/products/detail/nkk-switches/KP0115ANBKG03RGBP-3SJB/9463462
- NKK KPRGB series page: https://www.nkkswitches.com/products/illuminated-pushbutton/kp-series-miniature-audiovideo-4-pin-rgb-pushbuttons/
