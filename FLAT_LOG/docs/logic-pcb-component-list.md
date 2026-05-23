# Logic PCB Component List

This is the starting component list for the main/logic PCB schematic. It excludes the front-panel HMI components except for the connector to that board.

## 1. Architecture Boundary

### Main / Logic PCB

Contains:

- USB-C input and protection.
- 5 V system power path.
- 3.3 V regulator.
- ESP32-S3 module.
- Display/touch FFC connectors and backlight drive.
- Scanner connector, power switch, and UART level shifting.
- Front-panel HMI connector.
- Buzzer driver.
- Reset/boot/debug/test points.

### Front-Panel / UI PCB

Contains:

- 8x NKK RGB illuminated buttons.
- `TLC5947DAPRG4` RGB LED driver.
- `PCAL9555A` button input expander.
- JST-GH connector back to main PCB.

## 2. Main Logic PCB BOM - First Schematic Pass

Quantities are for one PCB.

### 2.1 MCU And RF

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | U_MCU | `ESP32-S3-WROOM-1U-N16R8` | Main MCU module, U.FL/I-PEX antenna connector, 16 MB flash, 8 MB PSRAM. |
| 1 | ANT_EXT | 2.4 GHz FPC/adhesive antenna, U.FL/I-PEX | Mechanical/electromechanical BOM item, not necessarily placed on PCB. Exact antenna TBD. |
| 1 | SW_BOOT | Momentary tact switch or test-pad only | GPIO0 boot mode. Optional if USB boot/test pads are enough. |
| 1 | SW_RESET | Momentary tact switch or test-pad only | EN/reset. Optional but useful during bring-up. |

Required passives:

- `R_MCU_EN`: 10 k ohm, 0603, 1%, 0.1 W. Pull `MCU_EN` to `SYS_3V3`.
- `C_MCU_EN`: 1 uF, X7R, 10 V or 16 V, 0603, 10%. EN/CHIP_PU RC delay to GND.
- `R_BOOT`: 10 k ohm, 0603, 1%, 0.1 W. Pull GPIO0/BOOT to `SYS_3V3`.
- `C_MCU_BULK`: 22 uF, X5R/X7R, 10 V or 16 V, 0805 or 1206, 20%. Local bulk near module 3V3 pin.
- `C_MCU_HF`: 100 nF, X7R, 16 V or 25 V, 0603, 10%. Local high-frequency bypass near module 3V3 pin.
- `R_USB_DN`, `R_USB_DP`: 22 ohm, 0603, 1%, 0.1 W. Series resistors near ESP32 pins GPIO19/GPIO20.
- `C_USB_DN_DNP`, `C_USB_DP_DNP`: small C0G/NP0, 50 V, 0402/0603, DNP. USB EMI tuning footprints to GND.
- `R_GPIO45_PD`: 10 k ohm, 0603, 1%, 0.1 W, optional/fitted. Keeps GPIO45 low for default 3.3 V VDD_SPI behavior.
- `R_GPIO46_PD`: 10 k ohm, 0603, 1%, 0.1 W, optional/fitted. Keeps GPIO46 low for deterministic USB/UART download mode when GPIO0 is held low.

### 2.2 USB-C Input And USB Data

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | J_USB | `USB4105-GF-A` | GCT USB-C receptacle, USB 2.0, right-angle. Good practical baseline. |
| 1 | U_USB_ESD | `USBLC6-2SC6` | ST USB 2.0 ESD protection for D+/D-/VBUS class use. |
| 2 | R_CC | 5.1 kΩ, 1% | CC1/CC2 Rd pulldowns for USB-C sink. |
| 2 | R_USB_SER | 22 Ω class | Optional USB D+/D- series resistors, place near MCU if used. |
| 1 | C_VBUS_BULK | 10 µF, X5R/X7R, 16 V or 25 V, 0805/1206, 10-20% | Optional USB VBUS bulk cap before eFuse if needed. |
| 1 | C_USB_DECOUPLE | 100 nF, X7R, 50 V, 0603, 10% | Local bypass around USB/eFuse input. |

### 2.3 5 V Input Protection / System Enable

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | U_EFUSE | `TPS259531DSGR` | TI TPS2595 eFuse, WSON-8, 2.7-18 V, adjustable current limit. |
| 1 | J_PWR_SW | 3-6 pin connector to panel power switch | Power switch drives eFuse enable/system enable; it does not carry full device current. Pin count depends on illumination. |
| 1 | SW_PWR | NKK `UB216KKG015C` | Locked polished power control. UB2, SPDT On-On, gold contacts, panel snap-in, solder lug, red LED nominal 1.85 V. |
| 1 | SW_SERVICE | `EG1218` series slide switch | Optional hidden service switch/fallback, not the primary visible power control. |
| 1 | TVS_VBUS | 5 V USB/power TVS | Exact part TBD; place near USB input. |
| 1 | C_SYS5_BULK | 10-22 µF, X5R/X7R, 16 V or 25 V, 0805/1206, 10-20% | Bulk on protected SYS_5V rail. Add more later only if testing says so. |

Required eFuse passives:

- Current-limit resistor.
- dV/dt or soft-start capacitor, if used.
- OVLO/UVLO divider, if used.
- Fault pull-up/test point, if fault pin is used.

### 2.4 3.3 V Buck Regulator

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | U_3V3 | `AP63203WU-7` | Diodes Inc. fixed 3.3 V, 2 A synchronous buck, TSOT26. |
| 1 | L_3V3 | 3.9 µH, shielded power inductor, Isat >= 3.5 A, Irms >= 2.5 A, low DCR | Datasheet value for AP63203 fixed 3.3 V output. Practical compact alternate: Bourns `SRP4020TA-3R3M` or TDK `SPM4020T-3R3M-LR`, both 3.3 µH shielded 4 mm class parts. |
| 1 | C_BOOT | 100 nF, X7R, 50 V, 0603, 10% | Bootstrap cap from BST to SW. |
| 1 | C_IN_3V3_1 | 10 µF, X5R/X7R, 25 V or 35 V, 1206, 10-20% | Buck input bulk cap. |
| 1 | C_IN_3V3_2 | 100 nF, X7R, 50 V, 0603, 10% | Buck input high-frequency decoupling. |
| 2 | C_OUT_3V3 | 22 µF, X5R/X7R, 16 V or 25 V, 1206, 10-20% | Buck output caps. Use two. |
| 1 | R_EN_3V3 | 100 kΩ, 0603, 1%, 0.1 W | Pull AP63203 EN to SYS_5V. |
| 1 | TP_3V3 | Test point | Strongly recommended. |

### 2.5 Display And Touch Connectors

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | J_TFT | Molex `54132-4062` or equivalent | 40-pin, 0.5 mm FFC/ZIF for Newhaven TFT. |
| 1 | J_CTP | Molex `52271-0679` or equivalent | 6-pin, 1.0 mm FFC/ZIF for Newhaven capacitive touch. |
| 1 | C_TFT_VDD_HF | 100 nF, X7R, 16 V or 25 V, 0603, 10% | TFT VDD/VDDI bypass near 40-pin FFC. |
| 1 | C_TFT_VDD_BULK | 1 uF, X7R, 10 V or 16 V, 0603/0805, 10% | TFT local logic/display bulk near 40-pin FFC. 4.7 uF is a fine upgrade if the footprint/BOM allows. |
| 1 | C_CTP_VDD_HF | 100 nF, X7R, 16 V or 25 V, 0603, 10% | Touch controller supply bypass near 6-pin FFC. |
| 1 | C_CTP_VDD_BULK | 1 uF, X7R, 10 V or 16 V, 0603/0805, 10% | Touch local bulk near 6-pin FFC. |
| 1 | U_BL | `STCS1APUR` | STCS1A constant-current LED driver, DFN8 3 mm x 3 mm. Use PowerSO-8 only if layout/assembly preference wins. |
| 1 | R_BL_SET | 0.68 ohm, 1%, 1206, >=0.25 W, low TCR preferred | Sets backlight to about 147 mA typical. Use 0.62 ohm for about 160 mA if full rated brightness is required. |
| 1 | C_BL_VCC_HF | 100 nF, X7R, 16 V or 25 V, 0603, 10% | STCS1A VCC bypass, close to VCC/GND. |
| 1 | C_BL_VCC_BULK | 1 uF, X7R, 16 V or 25 V, 0603/0805, 10% | Local backlight-driver supply bulk. |
| 1 | C_BL_DRAIN | 470 nF, X7R, 10 V or 16 V, 0603/0805, 10% | From STCS1A DRAIN / display LED cathode node to GND, close to driver. |
| 1 | C_BL_SLOPE | 10 nF, C0G/NP0 or X7R, 50 V, 0603, 5-10% | STCS1A slope-control capacitor. |
| 1 | R_BL_PWM_PD | 100 k ohm, 0603, 1%, 0.1 W | Pull PWM low so backlight stays off during ESP32 reset/boot. |
| 1 | R_BL_EN | 10 k ohm, 0603, 1%, 0.1 W | Pull STCS1A EN high to `SYS_5V`. |
| 1 | R_I2C_SCL_PU | 4.7 k ohm, 0603, 1%, 0.1 W | Shared I2C pull-up on main PCB. |
| 1 | R_I2C_SDA_PU | 4.7 k ohm, 0603, 1%, 0.1 W | Shared I2C pull-up on main PCB. |
| 1 | R_DISP_RST_PU | 10 k ohm, 0603, 1%, 0.1 W | Pull display/touch reset high; ESP32 drives low for reset. |
| 1 | R_TOUCH_INT_PU | 10 k ohm, 0603, 1%, 0.1 W, optional/fitted | Touch interrupt pull-up provision. |
| 1 | TP_LCD | Optional test pads | WR/DC/CS/RST/I2C useful for bring-up. |

Display notes:

- Logical `LCD_D0-D7` from ESP32 connect to Newhaven TFT `DB8-DB15`.
- Strap `IM0=1`, `IM1=0`, `IM2=0` for 8-bit 8080-II mode.
- `DISP_TOUCH_RST` drives both TFT `/RES` and CTP `/RESET` unless testing forces a split.
- Touch is I2C; TFT graphics are not I2C.
- Use the current 2025 Newhaven pinout for `NHD-2.8-240320AF-CSXP-FCTP`; older distributor PDFs may show the previous revision.

### 2.6 Scanner Interface

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | J_SCAN | JST-PH `B4B-PH-K-S` or compatible | 4-pin, 2.0 mm header matching Waveshare PH2.0 cable style. |
| 1 | U_SCAN_SW | `TPS22919DCKR` or `TPS22919DCKT` | 5 V scanner load switch. |
| 1 | U_SCAN_LVL | `TXU0202DCUR` | Fixed-direction dual-channel level shifter for UART, one channel each way. Easier than a DIR-controlled transceiver. |
| 1 | C_SCAN_IN | 100 nF, X7R, 16 V or 25 V, 0603, 10% | TPS22919 input bypass near IN/GND. |
| 1 | C_SCAN_OUT_HF | 100 nF, X7R, 16 V or 25 V, 0603, 10% | Scanner switched 5 V high-frequency bypass near connector. |
| 1 | C_SCAN_OUT_BULK | 10 µF, X5R/X7R, 16 V or 25 V, 0805/1206, 10-20% | Local scanner supply bulk near connector. |
| 2 | C_SCAN_LVL | 100 nF, X7R, 16 V or 25 V, 0603, 10% | One decoupler for TXU0202 VCCA and one for VCCB. |
| 2 | R_SCAN_SER | 100 Ω, 0603, 1%, 0.1 W | UART series resistors between connector and level shifter. |
| 1 | R_SCAN_SW_PD | 100 kΩ, 0603, 1%, 0.1 W | Pull TPS22919 ON low so scanner is off during ESP32 reset/boot. |
| 1 | R_SCAN_OE | 10 kΩ, 0603, 1%, 0.1 W | Pull TXU0202 OE high to `SYS_3V3`. |
| 1 | TP_SCANNER_5V | Test point | Harwin loop or 1 mm pad depending space. |
| 2 | TP_SCAN_UART | Test pad | Small signal pads for scanner TX/RX bring-up. |

Scanner connector pinout:

Match the exact Waveshare module silk/official pinout before assigning connector pin numbers. For Waveshare `Barcode Scanner Module (E)`, the official wiki pinout is:

1. `GND`
2. module `RX` = `SCAN_RX_TO_MODULE`
3. module `TX` = `SCAN_TX_FROM_MODULE`
4. `SCANNER_5V`

For the older Waveshare `Barcode Scanner Module` SKU 14810, verify the board silk because the quick-start guide says to connect by the labels, not by cable color.

### 2.7 Front-Panel HMI Connector

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | J_HMI | `BM14B-GHS-TBT(LF)(SN)` | JST-GH 14-pin top-entry header. |
| 1 | J_HMI_ALT | `SM14B-GHS-TB(LF)(SN)` | Side-entry alternate, choose one footprint/style. |
| 4 | R_HMI_LED_SER | 33 ohm, 0603, 1%, 0.1 W | Series damping for `LED_SIN`, `LED_SCLK`, `LED_LAT`, and `LED_BLANK` before the cable. |
| 1 | R_HMI_INT_PU | 10 k ohm, 0603, 1%, 0.1 W | Pull `HMI_INT` high to `SYS_3V3`; PCAL9555A interrupt is open-drain. |
| 1 | R_BTN_MULTI_WAKE_PU | 10 k ohm, 0603, 1%, 0.1 W | Pull direct multifunction wake line high on the main PCB. |
| 1 | C_HMI_3V3_CONN | 100 nF, X7R, 16 V or 25 V, 0603, 10%, optional | Small local connector-side bypass for the outgoing HMI 3.3 V rail. Main bulk remains on the front-panel PCB. |
| 1 | C_HMI_VLED_CONN | 1 uF, X7R, 16 V or 25 V, 0603/0805, 10%, optional | Small connector-side bypass for outgoing `VLED_5V`; LED bulk belongs on the front-panel PCB. |

Cable-side parts:

- Housing: `GHR-14V-S`.
- Crimps: `SSHL-002T-P0.2`.

Main PCB connector signals:

1. `VLED_5V`
2. `VLED_5V`
3. `SYS_3V3`
4. `GND`
5. `GND`
6. `I2C_SCL`
7. `I2C_SDA`
8. `HMI_INT`
9. `LED_SIN_HMI`
10. `LED_SCLK_HMI`
11. `LED_LAT_HMI`
12. `LED_BLANK_HMI`
13. `BTN_MULTI_WAKE`
14. `HMI_RESERVED`

### 2.8 Buzzer / Audio Feedback

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | BZ1 | TDK `PS1240P02BT` | Passive piezo transducer, 3 V rated, 4 kHz resonance, through-hole. Driven by ESP32 PWM. |
| 1 | R_BUZZ_SER | 100 Ω, 0603, 1%, 0.1 W | Series resistor between ESP32 `BUZZER_PWM` and piezo. Limits edge current/EMI. |
| 1 | R_BUZZ_BLEED | 1 MΩ, 0603, 1%, 0.1 W | Bleed resistor across piezo so it does not hold charge/pop unexpectedly. |
| 1 | TP_BUZZER_PWM | Test pad | Small signal pad on ESP32-side `BUZZER_PWM`. |

No MOSFET or flyback diode is needed for the selected passive piezo transducer. If a louder active magnetic buzzer is selected later, use a low-side MOSFET driver instead.

### 2.9 Debug And Test Points

| Qty | Reference | Part | Notes |
|---:|---|---|---|
| 1 | J_TAG / TP_SET | Tag-Connect footprint or grouped test pads | Optional but recommended. |
| many | TP_* | Keystone/Harwin/SMD test pads | Include generously. |

Minimum test points:

- `SYS_5V`
- `3V3`
- `GND`
- `EN`
- `GPIO0_BOOT`
- `USB_D+`
- `USB_D-`
- `I2C_SCL`
- `I2C_SDA`
- `SCAN_TX`
- `SCAN_RX`
- `SCANNER_5V`
- `LCD_WR`
- `LCD_CS`
- `LCD_DC`
- `DISP_TOUCH_RST`
- `LCD_BL_PWM`
- `HMI_INT`

## 3. Components Not On The Logic PCB

These belong on the front-panel/UI PCB:

| Qty | Part | Notes |
|---:|---|---|
| 8 | `KP0115ANBKG03RGBP-3SJB` | NKK RGB illuminated momentary buttons. |
| 1 | `TLC5947DAPRG4` | RGB LED driver for the 8 buttons. |
| 1 | `PCAL9555A` | I2C GPIO expander for button contacts. |
| 1 | `BM14B-GHS-TBT(LF)(SN)` or `SM14B-GHS-TB(LF)(SN)` | Matching JST-GH 14-pin header. |
| 1 | R_IREF for TLC5947 | Sets LED current. |
| several | I2C pull-ups / decoupling / test pads | Depending on final shared-bus strategy. |

## 4. Still To Decide Before PCB Order

- Exact 2.4 GHz internal antenna.
- Exact latching illuminated power button/switch style.
- Exact USB/power TVS part for VBUS.
- Exact display backlight current-driver package and current-set value.
- JST-GH top-entry vs side-entry for HMI connector.
- Whether reset/boot are physical switches or test pads only.
- Whether the rear power switch is board-mounted or cabled.

## 5. Sources

- ESP32-S3-WROOM-1U: https://www.espressif.com/en/products/modules/esp32-s3-wroom-1u
- GCT `USB4105-GF-A`: https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198441
- ST `USBLC6-2`: https://www.st.com/en/protections-and-emi-filters/usblc6-2.html
- TI `TPS259531DSGR`: https://www.ti.com/product/TPS2595/part-details/TPS259531DSGR
- Diodes Inc. `AP63203WU-7`: https://www.diodes.com/part/view/AP63203
- ST `STCS1A`: https://www.st.com/en/power-management/stcs1a.html
- TI `TPS22919DCKR`: https://www.ti.com/product/TPS22919/part-details/TPS22919DCKR
- TI `TXU0202DCUR`: https://www.ti.com/product/TXU0202
- JST-PH `B4B-PH-K-S`: https://www.digikey.com/en/products/detail/jst-sales-america-inc/B4B-PH-K-S/926613
