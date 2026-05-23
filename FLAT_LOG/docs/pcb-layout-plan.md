# Logic PCB Layout Plan

This document is the first layout plan for the Flat Log main logic PCB after schematic validation.

The schematic currently compiles with only accepted USB connector pin-type warnings:

- `GND contains IO Pin and Power Pin objects`
- `USB_VBUS contains IO Pin and Power Pin objects`

These are accepted because the USB-C connector library uses non-ideal electrical pin types. The circuit is not changed for these warnings.

## 1. Layout Philosophy

Treat the board as a compact embedded product, not a loose breakout board.

The routing priority is:

1. Power integrity and ground return paths.
2. ESP32-S3 RF/mechanical clearance.
3. USB D+/D- routing.
4. Buck converter hot-loop control.
5. Display parallel bus routing.
6. External connector usability and service access.
7. Cosmetics and silkscreen.

Do not begin with autorouting or arbitrary placement. Place the mechanical and electrical anchors first, then route the high-risk parts.

## 2. Recommended Stackup

Use a 4-layer PCB for v1.

| Layer | Use |
|---|---|
| L1 Top | Components, short signal routes, USB, buck, display bus escape. |
| L2 Inner 1 | Solid GND plane. Keep as continuous as possible. |
| L3 Inner 2 | Power distribution and some slow signals. Use pours/tracks for `SYS_5V`, `SYS_3V3`, `VLED_5V`, `SCANNER_5V`. |
| L4 Bottom | Secondary signal routing and local GND pours. |

Baseline manufacturing assumptions:

- Board thickness: 1.6 mm.
- Copper: 1 oz outer layers is fine.
- Solder mask: any.
- Minimum trace/space: use conservative 0.15 mm / 0.15 mm or larger unless the manufacturer allows tighter.
- Minimum via drill: 0.30 mm finished drill or larger where possible.

2-layer is possible, but for this design the 4-layer board is worth it because of Wi-Fi, USB, buck converter, display bus, and several external connectors.

## 3. Altium Setup Order

Before placement:

1. Create/open the `PcbDoc`.
2. Import the schematic:

```text
Design -> Update PCB Document
```

3. Accept/execute the ECO.
4. Define the board outline from the enclosure concept.
5. Define layer stack first.
6. Define design rules before routing.
7. Place mechanical anchors.
8. Place electrical blocks.
9. Route in priority order.

## 4. First Design Rules

Set these rules before serious routing.

### 4.1 Clearance

| Rule | Value |
|---|---:|
| Default clearance | 0.15 mm minimum, 0.20 mm preferred |
| Connector/mechanical clearance | Follow connector drawings |
| USB-C shell to copper | Keep sensible clearance unless intentionally connected through shield network |

### 4.2 Routing Widths

| Net Class | Width |
|---|---:|
| Default signal | 0.15-0.20 mm |
| I2C / GPIO / control | 0.15-0.20 mm |
| LCD parallel bus | 0.15-0.20 mm |
| USB D+/D- | impedance-controlled if possible; otherwise 0.15-0.20 mm as short matched pair |
| `USB_VBUS` | 0.50-0.80 mm minimum |
| `SYS_5V` | 0.50-1.00 mm where practical |
| `SYS_3V3` | 0.40-0.80 mm trunk, narrower branches acceptable |
| `VLED_5V` | 0.50-0.80 mm to HMI connector |
| `SCANNER_5V` | 0.40-0.60 mm |
| Backlight LED path | 0.40-0.60 mm |

### 4.3 Via Sizes

| Use | Suggested via |
|---|---|
| General signal | 0.60 mm pad / 0.30 mm drill |
| Power stitching | 0.70-0.80 mm pad / 0.30-0.40 mm drill |
| Thermal stitching under power parts | Follow package recommendations; use multiple vias |

### 4.4 Net Classes

Create these net classes:

- `USB_DIFF`: `USB_D_P`, `USB_D_N`, `USB_D_P_MCU`, `USB_D_N_MCU`
- `LCD_I80`: `LCD_D0-D7`, `LCD_WR`, `LCD_DC`, `LCD_CS`
- `I2C`: `I2C_SCL`, `I2C_SDA`
- `POWER_5V`: `USB_VBUS`, `SYS_5V`, `VLED_5V`, `SCANNER_5V`
- `POWER_3V3`: `SYS_3V3`
- `BACKLIGHT`: `BL_LED_K`, `BL_SENSE`

## 5. Placement Order

### 5.1 Mechanical Anchors First

Place these before anything else:

- USB-C connector at the enclosure edge.
- Power-switch harness connector.
- TFT 40-pin FFC connector.
- Touch 6-pin FFC connector.
- HMI JST-GH connector.
- Scanner PH connector.
- Mounting holes.
- ESP32-S3 module with antenna/u.FL access considered.
- Buzzer location with acoustic opening in mind.

Do not optimize electrical routing before these are mechanically plausible.

### 5.2 ESP32-S3 Module

Place the ESP32-S3 module so that:

- The u.FL antenna connector is accessible.
- The antenna cable can leave the board cleanly.
- The module is not boxed in by tall connectors.
- USB D+/D- from the USB-C area can reach GPIO19/GPIO20 cleanly.
- The display bus can fan out toward the TFT FFC without excessive crossing.

Keep a good ground plane under the module. Do not route noisy buck `SW` copper near the module or antenna cable path.

### 5.3 USB-C And eFuse

Recommended order:

```text
USB-C connector
  -> USB ESD / CC resistors
  -> eFuse input caps
  -> TPS259531 eFuse
  -> SYS_5V output caps
```

Placement rules:

- Put USB ESD close to the USB-C connector.
- Put CC pulldowns near the USB-C connector.
- Put eFuse input capacitor close to eFuse IN/GND.
- Put eFuse output capacitor close to eFuse OUT/GND.
- Keep `USB_VBUS` wide.
- Keep the shield RC/0R network near the USB-C connector shell pins.

### 5.4 AP63203 Buck Converter

Place as a tight power cell.

Critical loop:

```text
input cap -> AP63203 VIN/GND -> internal switch -> SW -> inductor -> output cap -> GND return
```

Placement rules:

- Input 100 nF and 10 uF caps close to VIN/GND.
- Bootstrap 100 nF close to BST/SW.
- Inductor close to SW.
- Output capacitors close to inductor output and GND.
- Keep the `SW` node small.
- Do not pour large copper on `SW`.
- Route FB from the output capacitor side, not from the noisy SW/inductor side.
- Keep FB away from SW copper.

### 5.5 Display And Touch

The display interface consumes many GPIOs, so connector placement matters.

Placement rules:

- Put the TFT FFC where the flex cable naturally reaches the display.
- Keep the 8-bit I80 bus reasonably short and direct.
- Route `LCD_D0-D7` as a grouped bus.
- Avoid running the LCD bus through the buck converter area.
- Place touch FFC close to the touch tail.
- Keep I2C pull-ups near the logic side, not at a random midpoint.
- Keep touch reset and interrupt away from noisy switching nodes.

### 5.6 Backlight Driver

Place STCS1A near the TFT backlight pins.

Placement rules:

- `BL_LED_K` path should be short and reasonably wide.
- `BL_SENSE` should be short and quiet.
- Place the 0.68 ohm sense resistor close to STCS1A FB/GND.
- Route sense resistor ground to the local ground plane with a short path.
- Keep `BL_SENSE` away from the buck `SW` node and display data bundle.

### 5.7 Scanner Block

Recommended order:

```text
SYS_5V
  -> TPS22919
  -> SCANNER_5V
  -> scanner connector

ESP32 UART
  -> TXU0202
  -> scanner connector
```

Placement rules:

- Put TPS22919 near the scanner connector.
- Put scanner output capacitors near the connector.
- Put TXU0202 between ESP32 and scanner connector, whichever gives cleaner routing.
- Keep UART traces simple; they are slow, but should not run through the buck hot area.
- Leave test pads reachable.

### 5.8 HMI Connector

Place the JST-GH connector according to the cable path to the front-panel PCB.

Placement rules:

- Put the 33 ohm LED serial resistors near the connector or near the ESP32 before the cable run.
- Keep `VLED_5V` and GND pins near each other in routing.
- Place `VLED_5V` local caps near the HMI connector.
- Keep I2C away from the buck SW node.
- Add clear pin-1 marking on silkscreen.

## 6. Routing Priority

Route in this order:

1. USB D+/D- from USB-C to ESD to ESP32.
2. Buck converter power cell.
3. eFuse and 5 V input/output power paths.
4. ESP32 power and decoupling.
5. Display parallel bus.
6. Backlight driver and LED path.
7. Scanner UART and switched 5 V.
8. HMI connector signals.
9. Buzzer.
10. Test pads and remaining slow nets.
11. Ground stitching vias and pours.

## 7. Grounding

Use L2 as an uninterrupted GND plane.

Rules:

- Do not split the main ground plane.
- Stitch GND generously around the board perimeter.
- Stitch near connectors.
- Put ground vias beside decoupling capacitor ground pads.
- Keep buck high-current return local and compact.
- Keep USB shield strategy separate from normal GND routing until the intentional shield network.

## 8. Test And Bring-Up Access

Keep these reachable with probes:

- `USB_VBUS`
- `SYS_5V`
- `SYS_3V3`
- `GND`
- `SYS_EN`
- `EFUSE_FLT`
- `BOOT_MODE`
- `MCU_EN`
- `USB_D_P_MCU`
- `USB_D_N_MCU`
- `I2C_SCL`
- `I2C_SDA`
- `MCU_SCAN_TX`
- `MCU_SCAN_RX`
- `SCANNER_5V`
- `LCD_BL_PWM`
- `BL_SENSE`
- `BUZZER_PWM`

Use small bare test pads for signals and larger loop/test pads for power rails where space allows.

## 9. First Layout Review Checklist

Before routing heavily, check:

- Board outline fits enclosure intent.
- USB-C is physically accessible.
- FFC connector orientations match the real flex cable direction.
- JST/PH cable exits are mechanically plausible.
- ESP32 u.FL connector is accessible.
- Buck converter placement is compact.
- eFuse path is clean and wide.
- Display bus does not cross the buck power cell.
- Test pads are not hidden under connectors or the display.
- Mounting holes have keepouts.
- Pin 1 markers exist on all polarized connectors.

Do a placement review before routing. A good placement saves hours; a bad placement makes every trace argue back.
