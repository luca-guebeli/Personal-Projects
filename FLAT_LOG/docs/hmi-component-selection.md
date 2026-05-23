# HMI Component Selection

This document defines the current v1 choice for the physical controls and user-visible LEDs.

## 1. HMI Direction

V1 should feel like a small countertop terminal, not a dev board in a printed box.

Current direction:

- Use real illuminated pushbuttons for all momentary front-panel controls.
- Keep the normal scan workflow physical.
- Use RGB illumination for user identity, selected state, queued/offline feedback, and wake/sleep breathing effects.
- Avoid separate decorative LEDs where the button illumination can carry the state.
- Put the HMI parts on a front-panel PCB so the main PCB remains mechanically stable.
- Use a momentary illuminated direction button rather than a maintained IN/OUT toggle switch.

## 2. Selected Momentary Button Family

### Baseline

**NKK KP01 series illuminated RGB pushbutton**

Preferred exact DigiKey part for general front-panel buttons:

- `KP0115ANBKG03RGBP-3SJB`

Variant considered:

- `KP0115ANBKG03RGBP-3SJCF11`

Use for:

- User 1
- User 2
- User 3
- User 4
- Direction IN/OUT
- Quantity +
- Quantity -
- Multifunction button

Count: 8 momentary buttons.

Why this is the baseline:

- RGB illumination is built into the switch.
- Long 4.5 mm travel gives a much better appliance/control-panel feel than tiny tact switches.
- Gold contacts and logic-level rating fit direct MCU input.
- High mechanical life according to NKK product information.
- Square caps can be arranged cleanly around the display.
- Same switch family for all momentary controls makes the front panel feel intentional.

Current preference:

- Click/tactile version, not the no-click version.
- Unmarked clear/white-diffuser square caps for the general buttons.
- Legends or icons can be handled with printed inserts, laser marking, enclosure legends, or a printed overlay.
- Avoid factory `ON/OFF` marked caps for every button because user buttons and quantity buttons need custom meaning.

Open item:

- Decide whether to use one `ON/OFF` marked variant for the multifunction button. This may look nice, but it could be confusing because the rear slide switch is the true hard power control.
- Verify exact cap/kit variant against the distributor listing before ordering.

### 2.1 DigiKey Variant Notes

`KP0115ANBKG03RGBP-3SJB` is the preferred baseline for all seven front buttons because DigiKey lists it as:

- SPST-NO, Off-Momentary.
- Through-hole.
- Square button.
- No actuator marking.
- Clear cap with white filter/diffuser.
- RGB LED.
- 100 mA at 12 VDC switch rating.
- 5,000,000-cycle mechanical and electrical life.

`KP0115ANBKG03RGBP-3SJCF11` appears electrically compatible, but DigiKey lists it with an `ON/OFF` actuator marking. Use only if that marking is desired for the multifunction button.

### Momentary Button Signal Plan

Each switch contact:

- One side to `GND`.
- One side to a front-panel I2C GPIO expander input with pull-up.
- Firmware debounce.
- Optional small RC or series resistor if testing shows noise/bounce issues.
- The multifunction button also connects to a direct ESP32-S3 wake-capable GPIO, in parallel with its expander input.

Each RGB LED:

- Driven by a dedicated LED driver, not directly by MCU GPIO.
- Default state after boot should be off or dim until firmware initializes.

## 3. LED Driver

### Baseline

**TI TLC5947 24-channel constant-current PWM LED driver**

Representative part:

- `TLC5947DAPR` for HTSSOP/package ease.
- `TLC5947RHBR` if a compact VQFN layout is preferred.

Why this is the baseline:

- 24 channels exactly covers up to eight RGB buttons.
- Eight RGB buttons require exactly 24 channels.
- Constant-current sink outputs make brightness more consistent than resistor-only GPIO driving.
- 12-bit PWM is enough for smooth fades, dim idle states, and per-user color tuning.
- Serial interface keeps MCU pin use low.

Signal plan:

- `LED_SIN`
- `LED_SCLK`
- `LED_LAT`
- `LED_BLANK`
- Optional `LED_SOUT` test/cascade pad.

Verified topology:

- The KPRGB LED arrangement is common-anode style with separate color cathodes.
- TLC5947 remains the correct driver because it is a constant-current sink device.
- Use 5 V for `VLED` to provide enough headroom for green/blue LED channels.
- Connect TLC5947 outputs to individual red/green/blue cathodes.

## 3.1 Button GPIO Expander

### Baseline

**NXP PCAL9555A 16-bit I2C GPIO expander**

Use:

- Read the eight front-panel button contacts.
- Provide interrupt-on-change to the ESP32-S3.
- Keep the front-panel harness compact.
- Avoid spending eight MCU GPIOs on low-speed buttons.

Why this is now the baseline:

- The 8-bit I80 display bus consumes a meaningful part of the ESP32-S3 GPIO budget.
- The front-panel PCB already has active electronics for RGB LED control.
- I2C expander input latency is irrelevant for human buttons.
- PCAL9555A includes weak pull-up support and interrupt features.

Signal plan:

- Shared `HMI_I2C_SCL`.
- Shared `HMI_I2C_SDA`.
- `HMI_INT` open-drain interrupt to ESP32-S3.
- Address pins strapped on the front-panel PCB.
- Optional reset tied to system reset or controlled from a spare/reset net if available.

## 4. IN/OUT Direction Button

### Baseline

**NKK KP01 RGB illuminated pushbutton**

Preferred exact part:

- `KP0115ANBKG03RGBP-3SJB`

Use:

- Front-panel `IN/OUT` direction control.

Why:

- Same button family as the rest of the HMI.
- Default direction can be IN on wake.
- OUT mode can be clearly indicated by red/amber illumination.
- Keeps the front panel visually cohesive.
- Reduces separate mechanical switch sourcing and enclosure cutout work.

Signal plan:

- One side of switch contact to `GND`.
- Other side to `BTN_DIRECTION` GPIO with pull-up.
- RGB LED channels driven by TLC5947.

Firmware behavior:

- On wake, direction defaults to IN.
- Short press toggles IN/OUT.
- Direction change commits any active item first.
- Direction button is off/dim/green-white in IN mode.
- Direction button is bright red/amber in OUT mode.
- Display always shows the current direction.

## 5. Rear Power Switch

### Baseline

**E-Switch EG1218 subminiature slide switch**

Use:

- Rear/side physical power switch.
- Drives the eFuse/system-enable signal, not raw high-current VBUS.

Why:

- Cheap and easy to source.
- Through-hole, mechanically forgiving.
- SPDT On-On.
- Small enough to hide on the rear or side.
- Good enough because it is not a frequent primary interaction.

Signal plan:

- Switch controls `SYS_EN` / eFuse enable logic.
- Optionally route the other throw to an ESP32 sense input if we want firmware to know the rear switch state before shutdown in a soft-latch variant.

## 6. Front-Panel PCB Concept

Put these on the front-panel PCB:

- 8x NKK KP01 RGB pushbuttons.
- TLC5947 LED driver.
- LED current-setting resistor.
- Front-panel connector to main PCB.
- Optional local decoupling and test pads.

Keep these on the main PCB:

- ESP32-S3 module.
- USB-C, power tree, eFuse, 3.3 V buck.
- Scanner connector.
- Display/touch connector, unless the display mechanically belongs on the front-panel PCB.

## 7. Front-Panel Connector Signals

Selected connector family:

- JST GH, 1.25 mm pitch.
- 14 positions.
- PCB header: `BM14B-GHS-TBT(LF)(SN)` for top-entry or `SM14B-GHS-TB(LF)(SN)` for side-entry.
- Cable housing: `GHR-14V-S`.
- Crimp contact: `SSHL-002T-P0.2`.

If the LED driver is on the front-panel PCB:

| Signal | Notes |
|---|---|
| `VLED` | 5 V LED common-anode supply for KP01 RGB LEDs. |
| `3V3` | Logic supply for TLC5947 if needed. |
| `GND` | Return. Use multiple pins if connector allows. |
| `HMI_I2C_SCL` | Shared I2C clock for front-panel expander. |
| `HMI_I2C_SDA` | Shared I2C data for front-panel expander. |
| `HMI_INT` | Open-drain interrupt from front-panel expander. |
| `LED_SIN` | MCU to TLC5947. |
| `LED_SCLK` | MCU to TLC5947. |
| `LED_LAT` | MCU to TLC5947. |
| `LED_BLANK` | MCU to TLC5947. |
| `BTN_MULTI_WAKE` | Direct active-low wake line from multifunction button to ESP32-S3. |
| `RESERVED_1` | Future/prototype. |
| `RESERVED_2` | Future/prototype. |

## 8. Visual State Model

User buttons:

- Idle available users: dim assigned color.
- Selected user: bright assigned color.
- Shared scope: no user button selected; multifunction button or display shows neutral white/blue.
- Offline queued event: selected scope can pulse amber or show an amber accent.
- Error: brief red pulse.

Quantity buttons:

- Normally dim white.
- Flash on press.
- Optional disabled/dim state when no active item exists.

Multifunction button:

- Sleep: off or very slow dim breathing if desired.
- Awake/shared: neutral white or blue.
- Settings/provisioning: blue/purple pulse.
- Recovery prompt: amber pulse.

Direction button:

- IN: off/dim neutral or dim green.
- OUT: bright red or amber.
- Direction change: brief confirmation flash.
- Error while OUT: red pulse but keep mode readable.

## 9. Alternatives

If NKK KP01 sourcing is annoying:

1. Use **E-Switch TL1265** illuminated tactile switches for a cheaper and easier-to-source front panel.
2. Use **C&K KSC** sealed tact switches under custom 3D printed caps with separate RGB LEDs/light pipes.
3. Use basic **E-Switch TL3305** tact switches only for early firmware bring-up, not final HMI.

If a maintained hardware IN/OUT state later feels preferable:

1. Use **E-Switch 100A** sealed SPDT toggle as the original direction-switch fallback.
2. Keep the display behavior and event model unchanged.

## 10. Sources

- NKK KP series overview: https://www.nkkswitches.com/products/illuminated-pushbutton/kp-series-miniature-illuminated-pushbutton-switches/
- NKK KP01-15ACAKP41F product details: https://www.nkkswitches.co.jp/product/detailed/KP01-15ACAKP41F.html
- NKK KP series DigiKey overview: https://www.digikey.com/en/product-highlight/n/nkk-switches/kp-series-illuminated-switches
- TI TLC5947 LED driver: https://www.ti.com/product/TLC5947
- NXP PCAL9555A GPIO expander: https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/low-voltage-16-bit-ic-bus-gpio-with-agile-i-o-interrupt-and-weak-pull-up:PCAL9555A
- E-Switch 100A sealed toggle: https://www.e-switch.com/product/100a-series-sealed-miniature-toggle-switch/
- E-Switch EG1218 slide switch: https://www.e-switch.com/product/eg-series-subminiature-slide-switch/
- E-Switch TL1265 fallback: https://www.e-switch.com/product/tl1265-series-illuminated-through-hole-tactile-switch/
- C&K KSC fallback: https://www.digikey.com/en/htmldatasheets/production/33193/0/0/1/ksc-series.html
