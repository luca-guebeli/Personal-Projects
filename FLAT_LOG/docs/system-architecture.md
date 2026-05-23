# Fridge Inventory Device System Architecture

## 1. Architecture Principle

The main PCB is the electrical center of the product. It contains the MCU module, power input/protection, regulators, debug/programming support, and connectors to all enclosure-facing submodules.

The enclosure-facing components should remain modular:

- Display module or display daughterboard.
- Barcode scanner module.
- User button board.
- Quantity/multifunction button board, if not part of the user button board.
- IN/OUT direction button.
- Status LED/light pipe board, if used.
- Buzzer/speaker.

This keeps the main PCB stable while the enclosure and front panel are iterated.

## 2. Top-Level Block Diagram

```text
                 +----------------------+
USB-C 5 V input -> Protection + switch  |
                 +----------+-----------+
                            |
                            v
                         5 V rail
                            |
             +--------------+--------------+
             |                             |
             v                             v
   Barcode scanner module          3.3 V regulator
   UART / trigger / status                 |
                                           v
                              +------------------------+
                              | Certified Wi-Fi MCU    |
                              | ESP32-S3 class module  |
                              +----+----+----+----+----+
                                   |    |    |    |
             +---------------------+    |    |    +----------------+
             |                          |    |                     |
             v                          v    v                     v
       Touch TFT display           Buttons / HMI          Buzzer / LEDs
```

## 2.1 Connectivity Environment

The intended kitchen location has weak Wi-Fi. A phone typically connects but reports only 1-2 bars out of 4.

Design consequences:

- Prefer an ESP32-S3 module variant with an external antenna connector.
- Use a hidden internal antenna where possible, rather than a bulky visible antenna.
- Place the antenna intentionally in the enclosure, away from the scanner, USB cable, large ground structures, and metal objects.
- Do not rely on always-online operation for basic scanning.
- Treat backend sync as eventually consistent.
- Show queued/offline status clearly on the display.
- Verify RF performance with the final enclosure installed in the actual kitchen location.

## 3. Power Architecture

### 3.1 Rails

| Rail | Nominal | Source | Main Loads |
|---|---:|---|---|
| VBUS_5V | 5 V | USB-C input after protection/switch | Scanner, 3.3 V regulator, optional LED power |
| 3V3 | 3.3 V | Buck regulator from VBUS_5V | MCU module, display logic, button pullups, level shifting |
| DISP_BL | 3.3 V or 5 V | TBD | Display backlight, if independently switched/dimmed |

### 3.2 Input And Protection

Main PCB should include:

- USB-C receptacle used as a 5 V sink.
- CC1/CC2 pulldown resistors.
- USB D+/D- routing for native USB programming/debug if supported by MCU.
- USB ESD protection.
- VBUS fuse, resettable fuse, or eFuse.
- Reverse/current/thermal protection if selected power switch topology benefits from it.
- Bulk capacitance near USB input and scanner connector.

### 3.3 On/Off Strategy Options

| Option | Description | Pros | Cons |
|---|---|---|---|
| True power switch | Physical switch disconnects VBUS_5V after input protection | Simple, intuitive, zero idle power after switch | MCU cannot gracefully shut down unless switch event is sensed before cutoff |
| Soft power latch | Button/switch controls load switch or power latch | Allows graceful shutdown and polished behavior | More circuitry, more design/debug effort |
| Hybrid | Rear true power switch plus front multifunction sleep/wake | Robust and understandable | Slightly more hardware |

Current preference: hybrid.

Implementation preference:

- Rear power switch controls the protected 5 V system rail enable, likely through an eFuse/load-switch enable pin.
- Front multifunction button is a low-voltage MCU input used for wake, sleep, Shared scope, cancel, and settings behavior.
- Active scan data is journaled immediately in firmware so an abrupt rear power-off does not lose the last scanned barcode.

### 3.4 Connectivity Robustness

The product should feel reliable even when Wi-Fi is marginal.

Required behavior:

- Scan events are accepted while offline.
- Committed events are written to local persistent storage before being considered safe.
- Network sync runs independently from the scan/UI path.
- Backend acknowledgements are tied to event_id.
- Failed sync attempts use bounded retry/backoff.
- UI shows at least three states: online/synced, online/syncing, offline/queued.

Preferred hardware support:

- Internal 2.4 GHz FPC/adhesive antenna via U.FL/I-PEX-style connector.
- Antenna mounted near the top/rear of the enclosure where possible.
- Avoid metal-filled/carbon-filled filament near the antenna.
- Keep the antenna coax short and mechanically restrained.
- Optional test firmware screen showing RSSI, connection state, and queued event count.

## 4. Main PCB Connector List

Connector names are provisional and intended to map naturally to schematic sheets.

### J1 - USB-C

| Signal | Notes |
|---|---|
| VBUS | 5 V input |
| GND | System ground |
| CC1/CC2 | Sink pulldowns |
| D+/D- | Native USB to MCU, with ESD protection |
| Shield | Chassis/ground strategy TBD |

### J2 - Barcode Scanner

Baseline assumption: Waveshare Barcode Scanner Module, or electrically similar low-cost decoded UART/USB scanner module under 120 USD. The connector should support simple module integration rather than premium OEM scan-engine FFC integration.

| Pin | Signal | Voltage Domain | Direction | Notes |
|---:|---|---|---|---|
| 1 | VBUS_5V_SW | 5 V | Output | Scanner supply, ideally switchable |
| 2 | GND | - | - | Return |
| 3 | SCAN_TX | TBD | Scanner to MCU | UART data from scanner |
| 4 | SCAN_RX | TBD | MCU to scanner | UART config/commands |
| 5 | SCAN_AUX_SPARE | TBD | MCU to scanner / spare | Optional future trigger/control, not exposed on baseline Waveshare 4-pin cable |
| 6 | SCAN_GOOD | TBD | Scanner to MCU | Optional good-read indication |
| 7 | SCAN_PWR_EN | 3.3 V | MCU/control | Optional scanner power enable or reserved |

Notes:

- Exact voltage levels depend on selected scanner module.
- If scanner UART is 5 V logic, level shifting is required.
- The Waveshare module ships with a documented 4-pin UART/power cable, so trigger/status are not baseline harness signals.
- UART logic level is not explicitly specified by Waveshare; include level-shift/protection provision.
- Use an accessible cable/connector family where possible, for example JST-PH/GH-style or a module-supplied pigtail, rather than a fragile custom FFC unless the selected scanner requires it.

### J3 - Display

Baseline assumption: high-quality IPS TFT with capacitive touch.

Preferred class: roughly 2.8 inch, 320 x 240 or 240 x 320, high brightness, capacitive touch, display interface over SPI or parallel, touch over I2C.

The connector shall remain provisional until the exact display is selected. A display with FFC/ZIF connection is preferred for a polished enclosure.

Current preferred implementation is a Newhaven-style 2.8 inch TFT with a conventional display controller and separate I2C capacitive touch controller. Riverdi-style intelligent displays remain an alternate path if the project later benefits from an HMI module with onboard graphics acceleration.

V1 keeps physical buttons as the primary interaction path. Touch is a secondary interface for provisioning, diagnostics, settings, and future UI exploration. A possible V2 could move toward an intelligent display and fewer/no physical buttons.

Current display bus preference: 8-bit I80/8080 parallel interface, plus I2C capacitive touch.

Rationale:

- Faster and more polished than SPI for LVGL-style UI.
- Much lower pin cost than 16-bit parallel.
- Official ESP-IDF `esp_lcd` supports I80 LCD buses on ESP32-S3.
- Leaves SPI buses available for expansion/debug if needed.

Verified Newhaven detail:

- In 8-bit 8080-II mode, use TFT `DB8-DB15`.
- Strap interface select as `IM0=1`, `IM1=0`, `IM2=0`.
- Touch `/RESET` needs a controlled reset; do not tie it directly to VCC.

| Pin | Signal | Voltage Domain | Notes |
|---:|---|---|---|
| 1 | 3V3 | 3.3 V | Display logic |
| 2 | GND | - | Return |
| 3 | SPI_SCLK | 3.3 V | Clock |
| 4 | SPI_MOSI | 3.3 V | Data to display |
| 5 | SPI_MISO | 3.3 V | Optional, touch/display readback |
| 6 | DISP_CS | 3.3 V | Display chip select |
| 7 | DISP_DC | 3.3 V | Data/command |
| 8 | DISP_RST | 3.3 V | Reset |
| 9 | DISP_BL_PWM | 3.3 V or driver input | Backlight dimming |
| 10 | TOUCH_SCL | 3.3 V | Capacitive touch I2C clock |
| 11 | TOUCH_SDA | 3.3 V | Capacitive touch I2C data |
| 12 | TOUCH_INT | 3.3 V | Optional touch interrupt |
| 13 | TOUCH_RST | 3.3 V | Optional touch reset |

If a parallel or RGB display is selected, this connector will be replaced by the exact FFC pinout from the display datasheet.

### J4 - User Button Board

Preferred first pass: front-panel HMI PCB with an I2C GPIO expander for button contacts and a dedicated RGB LED driver.

Selected momentary button baseline: 8x NKK KP01 RGB illuminated pushbuttons.

Selected LED driver baseline: TI TLC5947 24-channel constant-current PWM driver.

Selected button expander baseline: NXP PCAL9555A.

The final front-panel connector is defined in `pinout-and-connectors.md`; it includes shared I2C, HMI interrupt, TLC5947 serial signals, power, ground, and a direct multifunction wake line.

### J5 - Controls

| Pin | Signal | Notes |
|---:|---|---|
| 1 | 3V3 |
| 2 | GND |
| 3 | BTN_QTY_PLUS |
| 4 | BTN_QTY_MINUS |
| 5 | BTN_MULTI |
| 6 | BTN_DIRECTION |
| 7 | RESERVED |

The IN/OUT control is now a momentary illuminated direction button. On wake the direction defaults to IN; pressing the button toggles OUT mode. Final front-panel connector is defined in `pinout-and-connectors.md`.

### J6 - Feedback

| Pin | Signal | Notes |
|---:|---|---|
| 1 | VBUS_5V or 3V3 |
| 2 | GND |
| 3 | BUZZER_PWM |
| 4 | STATUS_LED |
| 5 | RESERVED |

### J7 - Debug / Programming

Options:

- USB-C native USB only.
- Tag-Connect footprint for JTAG/UART.
- 0.1 inch header for early bring-up.

Recommended: USB-C plus Tag-Connect footprint or small test pads.

Signals to expose:

- 3V3 sense/reference.
- GND.
- EN/RESET.
- BOOT/IO0 equivalent.
- UART TX/RX.
- JTAG signals if using ESP32-S3 USB/JTAG flow.

### J8 - Expansion / Reserved

Small optional connector exposing:

- 3V3.
- GND.
- I2C SDA/SCL.
- Spare GPIO.
- Optional 5 V.

This is not required for v1 function, but useful for a one-off polished unit.

## 5. GPIO Budget

Preliminary estimate:

| Function | GPIO Count |
|---|---:|
| 8-bit I80 display data/control/backlight | 13 |
| Touch + shared I2C | 3-4 |
| Scanner UART TX/RX | 2 |
| Scanner trigger/status/power enable | 2-3 |
| Front-panel button expander interrupt | 1 |
| Multifunction direct wake | 1 |
| HMI LED driver serial/control | 4 |
| Buzzer | 1 |
| Debug/strapping reserved | TBD |
| Expansion / true spares | Limited |

This is within ESP32-S3-class module capability, but GPIO is no longer abundant. The front-panel GPIO expander is part of the baseline to keep the pin budget and harness sane. Final pinout must avoid flash/PSRAM, USB, strapping, and restricted pins.

## 6. Firmware State Machine

```text
OFF
 |
 | physical power switch on
 v
BOOT
 |
 v
PROVISIONING_REQUIRED? ---- yes ---> PROVISIONING
 |
 no
 v
IDLE_SHARED
 |
 | user button
 v
IDLE_USER
 |
 | scan
 v
ACTIVE_ITEM
 |
 | +1/-1
 v
ACTIVE_ITEM
 |
 | next scan / owner change / direction change / timeout / sleep
 v
COMMIT_EVENT
 |
 v
SYNC_QUEUE
 |
 v
IDLE_SHARED or IDLE_USER
 |
 | 30 s inactivity
 v
SLEEP
 |
 | multifunction press / button activity
 v
IDLE_SHARED
```

## 7. Event Handling

Firmware should treat every committed scan as a durable event.

Active item handling:

- When a barcode is scanned, the active item is immediately written to a persistent active-item journal.
- +1/-1 updates also update the journal.
- Owner or direction changes commit or cancel according to the UX state machine, then clear or replace the journal.
- On boot after abrupt power loss, firmware checks the journal and applies the defined recovery policy.

Minimum event fields:

- device_id
- event_id
- owner_scope
- direction
- barcode
- quantity
- device timestamp or uptime
- firmware version

Event lifecycle:

1. Active item is committed.
2. Event is written to persistent local queue.
3. Network task sends event to backend.
4. Backend acknowledges event_id.
5. Firmware marks event as synced.
6. Synced events may be retained for a limited debug/history window.

## 8. UI Information Model

Awake idle screen should show:

- Owner scope.
- IN/OUT direction.
- Wi-Fi/backend status.
- Ready-to-scan state.

Active item screen should show:

- Owner scope.
- IN/OUT direction.
- Product name or barcode if unknown.
- Quantity.
- Pending/saved/offline status.

Error screen should show:

- Owner scope and direction remain visible.
- Short error message.
- Recoverable action where possible.

## 9. Initial Engineering Recommendations

- Use direct GPIO for buttons in Rev A unless pin pressure becomes real.
- Prefer a scanner module with 3.3 V UART if possible.
- Include a controllable scanner power rail.
- Include display backlight PWM or load switch.
- Keep display and scanner connectors near enclosure cable exits.
- Keep external antenna placement mechanically planned from the beginning.
- Include more test pads than feel strictly necessary.

## 10. Decisions To Make Next

1. Select MCU module family and hidden internal antenna strategy.
2. Decide display size and connection style.
3. Shortlist scanner modules and identify electrical interface.
4. Choose final front-panel layout and legends.
5. Confirm rear power switch implementation around the eFuse enable.
6. Define Wi-Fi provisioning method.
