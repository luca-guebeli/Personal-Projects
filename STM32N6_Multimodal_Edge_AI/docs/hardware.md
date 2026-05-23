# Hardware Notes

This file tracks the actual hardware used for the project. Keep it factual: exact labels, board revisions, jumper settings, cables, and anything that affects reproducibility.

## Inventory

| Component | Exact Part / Revision | Role | Status | Notes |
| --- | --- | --- | --- | --- |
| STM32N6 board | NUCLEO-N657X0-Q / MB1940 | Main edge AI target | In hand | Confirm board revision from silkscreen or product sticker |
| Camera module | B-CAMS-IMX / MB1854 | Vision input | In hand | 5-Mpx RGB CMOS image sensor, dual-lane MIPI CSI-2 output, 22-pin FFC, M12 lens, IMU, and ToF sensor |
| MEMS microphone(s) | X-NUCLEO-CCA02M2 | Audio input | In hand | Two MP34DT06J digital MEMS microphones; supports synchronized acquisition of up to 4 microphones with coupon boards |
| USB cable | TBD | Power/debug/programming | TBD | Confirm data-capable cable |
| microSD card | TBD | Optional logging/storage | TBD | Useful for frame/audio captures |
| Display | TBD | Optional visual output | TBD | Useful if using a Discovery kit with LCD |

## Interfaces To Confirm

### Camera
- B-CAMS-IMX uses a Sony 5-Mpx RGB CMOS image sensor on the MB1854 accessory board
- Interface type: dual-lane MIPI CSI-2 through the NUCLEO-N657X0-Q CN6 22-pin FFC connector
- Camera control path: I2C2 on PB10/PB11
- Camera reset/enable path: NRST_CAM on PO5 and PWR_EN on PA0
- Supported resolutions and pixel formats
- Driver source: start with ST's x-cube-n6-camera-capture package or a STM32CubeN6 DCMIPP example
- Buffer location: internal SRAM, PSRAM, or external memory
- Whether the B-CAMS-IMX ToF sensor can help separate the centered foreground object from the background

### Audio
- Microphone type: X-NUCLEO-CCA02M2 digital MEMS microphones
- On-board microphone part: MP34DT06J
- Peripheral path to confirm on the STM32N6 board: I2S, SPI, DFSDM, or SAI
- Sample rate and bit depth
- Number of channels
- DMA buffer strategy

### Debug And Power
- ST-LINK detection
- Boot mode / jumper settings
- Power source and current limits
- Serial logging path

## Known Platform Notes

The STM32N6 family is designed for edge AI and multimedia workloads. ST documents a camera pipeline with MIPI CSI-2 and image signal processing, plus AI tooling for deploying neural networks to the Neural-ART accelerator.

If the board is the STM32N6570-DK Discovery kit, ST's data brief lists a camera module connector, one MEMS digital microphone, an audio MEMS daughterboard expansion connector, external flash/PSRAM, an LCD, and an on-board STLINK-V3EC debugger.

The B-CAMS-IMX module is a strong match for the first vision demo because it provides the camera input, an IMU, and a multizone direct ToF sensor in the same bundle. The ToF sensor may become useful later for center-object foreground/background separation.

The X-NUCLEO-CCA02M2 gives the project a clean audio path for later wake, trigger, or sound-event experiments. The first milestone should still be independent audio capture before mixing audio into the camera demo.

## Open Questions

- Which exact NUCLEO-N657X0-Q board revision is this?
- Which STM32N6 pins and peripheral instance are used for the X-NUCLEO-CCA02M2?
- Should the first outline demo be class-agnostic, or should it focus on a small set of objects?
- Which objects should appear in the first dataset: hands, desk objects, electronics parts, or something else?
- Should the first demo prioritize vision only, or use audio as a trigger?

## References

- [STM32N6 series - STMicroelectronics](https://www.st.com/en/microcontrollers-microprocessors/stm32n6-series.html)
- [NUCLEO-N657X0-Q product page - STMicroelectronics](https://www.st.com/en/evaluation-tools/nucleo-n657x0-q.html)
- [NUCLEO-N657X0-Q user manual - STMicroelectronics](https://www.st.com/resource/en/user_manual/um3417-stm32n6-nucleo144-board-mb1940-stmicroelectronics.pdf)
- [STM32N6570-DK data brief - STMicroelectronics](https://www.st.com/resource/en/data_brief/stm32n6570-dk.pdf)
- [B-CAMS-IMX data brief - STMicroelectronics](https://www.st.com/resource/en/data_brief/b-cams-imx.pdf)
- [B-CAMS-IMX user manual - STMicroelectronics](https://www.st.com/resource/en/user_manual/um3354-camera-module-for-stm32-boards-stmicroelectronics.pdf)
- [X-NUCLEO-CCA02M2 product page - STMicroelectronics](https://www.st.com/en/evaluation-tools/x-nucleo-cca02m2.html)
- [x-cube-n6-camera-capture - STMicroelectronics GitHub](https://github.com/STMicroelectronics/x-cube-n6-camera-capture)
