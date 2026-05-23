# Fridge Inventory Device Specification

## 1. Product Intent

The device is a countertop barcode terminal for a shared flat fridge. It should make it fast to log food items without opening an app at the fridge. The product is a one-off polished home project, but it should be designed with an industrial mindset: modular hardware, robust firmware, clear service/debug access, and a well-defined backend contract.

The device records scan events. It does not attempt to be the source of truth for inventory state. Inventory is derived by the backend from immutable events.

## 2. Current Product Scope

### 2.1 Included

- Countertop enclosure.
- USB-C powered.
- Physical on/off switch.
- Multifunction wake/sleep/shared button.
- Barcode scanner module.
- High-quality color display capable of showing product and user names.
- Capacitive touch support if available without compromising the physical-button workflow.
- Four user buttons.
- Shared inventory scope.
- IN/OUT direction button.
- +1/-1 quantity controls.
- Wi-Fi backend connection.
- Web/app inventory view.
- Automatic commit without a confirm button.
- Sleep after inactivity.
- Robust behavior in weak kitchen Wi-Fi conditions.

### 2.2 Excluded From First Build

- Battery operation.
- Camera-based barcode decoding.
- Full inventory editing on the device.
- Multi-unit manufacturing optimization.
- Bare RF design.
- Touch-only operation without physical buttons.

## 3. Core UX

### 3.1 Owner Scope

The device supports five owner scopes:

- Shared
- User 1
- User 2
- User 3
- User 4

On wake, the default scope is Shared. If the user scans without pressing a user button, the event is assigned to Shared.

### 3.2 Direction

The device has a physical direction button.

- IN means items are added to the selected inventory scope.
- OUT means items are removed from the selected inventory scope.
- On wake, the default direction is IN.
- Pressing the direction button toggles OUT mode.
- The direction button illumination indicates OUT mode.
- The display shall always show the active direction, so the LED is helpful but not the only indication.

### 3.3 Scan Flow

Normal flow:

1. Device is awake.
2. Active owner scope is shown.
3. Active IN/OUT direction is shown.
4. User scans an item.
5. Device displays product name and quantity x1.
6. User may press +1/-1 to adjust quantity.
7. The user scans the next item or stops interacting.
8. The previous active item is automatically committed.

No confirm button is required.

### 3.4 Active Item Commit Rules

An active scanned item shall be committed when any of the following occurs:

- A new barcode is scanned.
- The inactivity timeout expires.
- The active owner scope changes.
- The IN/OUT direction changes.
- The device enters sleep.
- The device is powered off, if firmware has enough time to persist the event.

### 3.5 Inactivity And Sleep

After 30 seconds without scan, button, or switch activity:

- The active item is committed, if present.
- The display enters sleep/off/dim mode.
- Scanner power may be disabled.
- MCU may enter light sleep or low-power idle.

Since the device is USB-C powered, sleep is primarily for polish, display lifetime, and thermal/idle behavior rather than battery conservation.

### 3.6 Multifunction Button

Proposed behavior:

| Device State | Short Press | Long Press |
|---|---|---|
| Sleep | Wake to Shared scope | Wake and enter setup/settings mode |
| Awake idle | Return to Shared scope | Enter sleep |
| Active item shown | Commit active item and return to Shared scope | Cancel active item |
| Error shown | Dismiss error | Enter sleep |

This behavior may be revised after UI prototyping.

## 4. Functional Requirements

| ID | Requirement |
|---|---|
| UX-001 | The device shall support four individual users and one Shared inventory scope. |
| UX-002 | On wake, the default owner scope shall be Shared. |
| UX-003 | The device shall always show the active owner scope while awake. |
| UX-004 | The device shall always show the active IN/OUT direction while awake. |
| UX-005 | A scanned item shall default to quantity 1. |
| UX-006 | +1 and -1 controls shall adjust the active scanned item quantity. |
| UX-007 | The user shall not need to confirm a scan. |
| UX-008 | The device shall automatically commit active items according to the commit rules. |
| UX-009 | The device shall enter sleep after 30 seconds of inactivity. |
| UX-010 | The display shall be able to show product names and user names. |
| UX-011 | The display shall show clear success, pending, offline, and error states. |
| UX-012 | Touch input may be used for secondary screens such as settings, diagnostics, Wi-Fi setup, and inventory browsing. |
| UX-013 | Normal scan operation shall remain usable with physical controls only. |
| UX-014 | On wake, the default direction shall be IN. |
| UX-015 | The direction control shall be a momentary illuminated button, not a maintained switch. |
| UX-016 | Pressing the direction button shall toggle between IN and OUT modes. |
| UX-017 | The direction button shall illuminate clearly when OUT mode is active. |
| HW-001 | The device shall be a countertop device. |
| HW-002 | The device shall be powered by USB-C only. |
| HW-003 | The device shall include a physical on/off switch. |
| HW-004 | The main PCB shall contain MCU, power management, protection, debug/programming, and connectors. |
| HW-005 | Barcode scanner, display, buttons, switches, and indicators may be submodules connected to the main PCB. |
| HW-006 | The design shall use a certified wireless MCU module rather than bare RF silicon. |
| FW-001 | Firmware shall store scan events persistently before or during network transmission. |
| FW-002 | Firmware shall tolerate temporary Wi-Fi/backend outages. |
| FW-003 | Firmware shall use monotonic event IDs to support deduplication. |
| FW-004 | Firmware shall expose a debug/programming interface. |
| FW-005 | Firmware should support OTA updates if implementation effort remains reasonable. |
| FW-006 | Firmware shall journal the active scanned item to persistent storage immediately after scan, before waiting for timeout or next scan commit. |
| FW-007 | Firmware shall update the active item journal when quantity, owner scope, or direction changes. |
| FW-008 | On boot, firmware shall recover or safely discard any active item journal according to a defined recovery policy. |
| CON-001 | The device shall be designed for weak kitchen Wi-Fi where a phone may show only 1-2 bars out of 4. |
| CON-002 | The device shall allow scanning to continue while temporarily offline. |
| CON-003 | The display shall clearly distinguish synced events from locally queued events. |
| CON-004 | The hardware design shall prefer an antenna strategy with strong RF performance while avoiding a bulky visible antenna. |
| CON-005 | Wi-Fi performance shall be verified in the intended kitchen location before final enclosure closure. |
| BE-001 | The backend shall receive immutable scan events from the device. |
| BE-002 | The backend shall derive inventory from events. |
| BE-003 | The backend shall allow manual correction of inventory mistakes. |
| BE-004 | The backend shall perform or cache barcode-to-product lookup. |

## 5. Preliminary Hardware Architecture

```text
USB-C input
   |
Input protection / fuse / power switch
   |
5 V rail
   |--------------------> Barcode scanner module
   |
3.3 V regulator
   |
Certified Wi-Fi MCU module
   |-- Display connector
   |-- Barcode scanner connector
   |-- User button connector(s)
   |-- IN/OUT direction button connector
   |-- +1/-1 connector
   |-- Multifunction button connector
   |-- LED/buzzer connector
   |-- Debug/programming connector
   |-- Optional expansion connector
```

## 6. Preferred Engineering Direction

### 6.1 MCU

Baseline direction: ESP32-S3 module with external antenna option, using a hidden internal antenna if possible.

Rationale:

- Integrated Wi-Fi.
- Native USB for programming/debugging.
- Enough GPIO for the intended controls.
- Sufficient processing headroom for UI, networking, event queue, and OTA.
- Certified module reduces RF design risk.
- External antenna option improves placement freedom in weak kitchen Wi-Fi.
- "External antenna" means external to the module, not necessarily outside the enclosure.
- Preferred industrial-looking implementation is an internal 2.4 GHz FPC/adhesive antenna connected by U.FL/I-PEX-style coax.

### 6.2 Display

Baseline direction: high-quality IPS TFT with capacitive touch, roughly 2.8 inches, at least 320 x 240.

Current preferred display class: Newhaven-style 2.8 inch IPS TFT with capacitive touch, ST7789-class controller, and I2C capacitive touch controller.

Current alternate display class: Riverdi-style intelligent EVE/BT817 display module if a more self-contained industrial HMI module becomes desirable.

V1 philosophy: physical controls remain primary. Touch is included for flexibility, diagnostics, provisioning, and future UI experiments, but the normal scan workflow must not depend on touch.

Possible V2 direction: intelligent display HMI with reduced or removed physical buttons.

Rationale:

- Enough room for product names, user names, direction, quantity, status, and icons.
- More flexible and polished than a small monochrome OLED.
- IPS panel improves viewing angle for countertop use.
- Capacitive touch enables richer setup, diagnostics, and future UI without replacing physical buttons.
- 2.8 inches is large enough for product names while still compact.

Display implementation options:

| Option | Notes |
|---|---|
| SPI TFT + I2C capacitive touch | Simplest wiring and firmware. Good enough if UI mostly updates regions rather than full-screen animation. |
| 8/16-bit parallel TFT + I2C capacitive touch | Faster display updates, more GPIO and routing. Good option for a premium UI on ESP32-S3. |
| RGB TFT + I2C capacitive touch | Highest flexibility/framebuffer-style UI, but uses many pins and requires more careful memory/bandwidth planning. |
| Intelligent display module | Display has its own graphics controller. Very polished, but can constrain the UI programming model. |

### 6.3 Scanner

Baseline direction: Waveshare Barcode Scanner Module or equivalent low-cost decoded 1D/2D barcode scanner module with UART interface.

Rationale:

- Avoids camera/vision complexity.
- More appliance-like behavior.
- UART protocol is easy to isolate and test.
- Scanner is not a prestige component for this product; low cost and easy integration matter more than premium OEM performance.
- Target scanner cost is under 120 USD, with cheaper preferred if documentation and integration remain acceptable.
- Common connectors, simple pinout, and published UART/USB documentation are preferred over proprietary OEM scan engine integration.
- Waveshare Barcode Scanner Module is the selected v1 baseline, pending bench validation.

### 6.4 Main PCB Modularity

The main PCB should avoid mechanically overcommitting to enclosure-facing parts. Display, scanner, buttons, and indicators should connect by cable or small daughterboards where practical.

This supports enclosure iteration without requiring a main PCB respin.

## 7. Backend Event Contract

Preliminary event shape:

```json
{
  "device_id": "fridge-terminal-001",
  "event_id": 12345,
  "owner_scope": "shared",
  "direction": "in",
  "barcode": "7612345678901",
  "quantity": 2,
  "created_at_device": "2026-05-01T18:42:00+02:00"
}
```

Open question: device timestamps may be unavailable before network time sync. The backend should be able to accept events with device uptime or server receive time.

## 8. Open Decisions

| ID | Topic | Options / Notes |
|---|---|---|
| OD-001 | Exact MCU module | ESP32-S3-WROOM-1, ESP32-S3-WROOM-1U, ESP32-S3-MINI, other module. |
| OD-002 | Antenna strategy | Current preference: ESP32-S3 module with U.FL/I-PEX antenna connector and hidden internal FPC/adhesive antenna. Avoid bulky visible whip antenna unless RF testing proves it necessary. |
| OD-003 | Display size | Current preference: about 2.8 inch IPS TFT with capacitive touch. 3.5 inch only if UI benefit justifies enclosure size. |
| OD-004 | Display connection | SPI or parallel TFT over FFC/ZIF, plus I2C touch. Consider intelligent display module as premium alternative. |
| OD-005 | Scanner module | Current baseline: Waveshare Barcode Scanner Module. Need validate UART voltage level, protocol, trigger mode, and scan geometry. |
| OD-006 | Button topology | Current baseline: PCAL9555A I2C expander for 8 button inputs, plus direct multifunction wake line. |
| OD-007 | User indication | Backlit buttons, RGB LEDs, display-only, or combination. |
| OD-008 | On/off topology | True VBUS cutoff vs soft power/latching switch. |
| OD-009 | Wi-Fi provisioning | BLE provisioning, captive portal, USB serial setup, or app-assisted setup. |
| OD-010 | Enclosure service access | External USB only, hidden debug port, removable bottom panel. |

## 9. Next Step

Create a system architecture and interface list:

- Choose the provisional MCU module family.
- Choose the display class and connector style.
- Choose barcode scanner interface assumptions.
- Define every main PCB connector.
- Define required GPIO, power rails, voltage levels, and protection needs.
