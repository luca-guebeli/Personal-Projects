# Camera Bring-Up: NUCLEO-N657X0-Q + B-CAMS-IMX

## Goal

Prove that the B-CAMS-IMX camera works on the NUCLEO-N657X0-Q before writing custom vision firmware.

The fastest validation path is ST's `x-cube-n6-camera-capture` package. It provides ready-to-flash NUCLEO-N657X0-Q binaries that expose the camera as a USB UVC webcam.

## Known Hardware

- Board: NUCLEO-N657X0-Q / MB1940
- Camera: B-CAMS-IMX / MB1854
- Camera connector on NUCLEO: CN6, 22-pin FFC, MIPI CSI-2
- Debug/programming connector: CN10, STLINK-V3EC USB-C
- User USB / UVC streaming connector: CN8, USB-C

## Pre-Flight Checklist

- Leave the X-NUCLEO-CCA02M2 disconnected for the first camera test.
- Power off the NUCLEO before inserting or removing the B-CAMS-IMX FFC cable.
- Check the FFC orientation visually against the silkscreen and ST user manuals.
- Lock the ZIF connector gently; do not force the cable.
- Use a USB-C cable with data support for CN10.
- Use a second USB-C data cable from CN8 to the PC for UVC streaming.
- Keep the board on a stable, powered USB port. Avoid low-power hubs during first bring-up.

## Route A: Fast Camera Proof With ST Prebuilt Firmware

Use this route first.

1. Download `x-cube-n6-camera-capture` from ST's GitHub repository.
2. Connect B-CAMS-IMX to the NUCLEO CN6 camera connector with the board unpowered.
3. Connect CN10 to the PC for ST-LINK programming and power.
4. Set the board to development boot mode.
   - On STM32N6, development boot is selected when `BOOT1 = 1`.
   - Flash boot is selected when `BOOT0 = 0` and `BOOT1 = 0`.
   - On the NUCLEO board these are configured with JP1 (`BOOT0`) and JP2 (`BOOT1`).
5. Open STM32CubeProgrammer and connect over ST-LINK / SWD.
6. Program one of the NUCLEO prebuilt hex files:
   - `Binary/NUCLEO-N657X0-Q/x-cube-n6-camera-capture-front-nucleo.hex`
   - `Binary/NUCLEO-N657X0-Q/x-cube-n6-camera-capture-rear-nucleo.hex`
7. Set the board back to flash boot mode.
8. Power-cycle the board.
9. Connect CN8 to the PC for USB UVC streaming.
10. Open the Windows Camera app, OBS, VLC, or another webcam viewer.
11. Confirm that a live image appears.

Expected result:
- The board enumerates as a USB camera.
- The camera stream is visible on the PC.
- At least one of the front/rear firmware orientations gives the expected image orientation.

## Flashing The Hex With STM32CubeProgrammer

### Option 1: GUI

1. Open STM32CubeProgrammer.
2. Select `ST-LINK`.
3. Set the board to development boot mode.
4. Connect CN10 to the PC.
5. Click `Connect`.
6. Open the external loader settings and enable the NUCLEO loader:
   - `MX25UM51245G_STM32N6570-NUCLEO.stldr`
7. Go to `Erasing & Programming`.
8. Browse to the camera capture hex file:
   - `Binary/NUCLEO-N657X0-Q/x-cube-n6-camera-capture-front-nucleo.hex`
   - or `Binary/NUCLEO-N657X0-Q/x-cube-n6-camera-capture-rear-nucleo.hex`
9. Leave the address field alone for `.hex` files. Intel HEX files include address records.
10. Enable verification if available.
11. Click `Start Programming`.
12. Disconnect, set the board to flash boot mode, power-cycle, and connect CN8 for webcam streaming.

### Option 2: PowerShell / CLI

Adjust the two paths for your machine:

```powershell
$loader = "C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\ExternalLoader\MX25UM51245G_STM32N6570-NUCLEO.stldr"
$hex = "C:\path\to\x-cube-n6-camera-capture\Binary\NUCLEO-N657X0-Q\x-cube-n6-camera-capture-front-nucleo.hex"

STM32_Programmer_CLI.exe -c port=SWD mode=HOTPLUG -el $loader -hardRst -w $hex -v
```

Use the `rear` hex instead if the image orientation is wrong:

```powershell
$hex = "C:\path\to\x-cube-n6-camera-capture\Binary\NUCLEO-N657X0-Q\x-cube-n6-camera-capture-rear-nucleo.hex"
STM32_Programmer_CLI.exe -c port=SWD mode=HOTPLUG -el $loader -hardRst -w $hex -v
```

If PowerShell cannot find `STM32_Programmer_CLI.exe`, run the command from the STM32CubeProgrammer `bin` folder or add that folder to `PATH`.

## Route B: Source-Level Camera Bring-Up

Use this after Route A works.

1. Open the NUCLEO-N657X0-Q project from `x-cube-n6-camera-capture` in STM32CubeIDE.
2. Build and run the project in development mode.
3. Confirm serial logs on the ST-LINK virtual COM port.
4. Keep the USB UVC output working while adding small debug prints.
5. Locate the camera probe path and confirm the IMX sensor ID is read successfully.
6. Locate the frame buffer path and document:
   - input resolution
   - output stream format
   - buffer address
   - buffer ownership
   - DCMIPP crop/decimation/downscale settings

## What To Record

Add these results to this file once tested:

| Check | Result | Notes |
| --- | --- | --- |
| Board revision | TBD | Silkscreen or sticker |
| Camera cable orientation | TBD | Photo recommended |
| CN10 ST-LINK connects | Passed | STM32CubeProgrammer could program the board |
| Firmware flashed | Passed | `x-cube-n6-camera-capture-front-nucleo.hex` |
| CN8 UVC enumerates | Passed | USB camera appeared in Windows Device Manager |
| Live image visible | Passed | Camera stream working on PC |
| Best orientation | Front | `front` hex has correct orientation |
| Serial log visible | TBD | COM port and settings |

## Stream Size And Frame Rate

ST's camera-capture firmware advertises multiple USB UVC stream sizes at 30 fps:

- 224x224 YUV422 at 30 fps
- 256x256 YUV422 at 30 fps
- 480x480 YUV422 at 30 fps
- 640x480 YUV422 at 30 fps
- 800x480 YUV422 at 30 fps

If a host application is choppy, select a smaller stream size first. For the Python outline prototype, use a smaller capture size and lower processing scale before changing firmware.

## Useful Debug Clues

If STM32CubeProgrammer cannot connect:
- Confirm CN10 is connected, not only CN8.
- Put the board in development boot mode.
- Try `HOTPLUG` mode in STM32CubeProgrammer.
- Check that the ST-LINK target power/status LED is healthy.

If STM32CubeProgrammer shows `Warning: The core is locked up`:
- Do not assume the flash failed if programming and verification completed successfully.
- Check the log for messages such as `Download verified successfully`, `File download complete`, or a successful verify step.
- Set the board back to flash boot mode, power-cycle, and test the USB camera path.
- If the application does not run, repeat programming in development boot mode with the NUCLEO external loader enabled.
- If the warning appears together with failed erase/program/verify messages, treat it as a real flashing failure.

If the firmware flashes but no webcam appears:
- Confirm CN8 is connected with a data-capable USB-C cable.
- Power-cycle after switching back to flash boot.
- Try the other front/rear NUCLEO hex file.
- Check Windows Device Manager for USB camera enumeration.
- Check whether the ST-LINK virtual COM port prints application logs at 115200 8N1.
- Re-flash with verification enabled and save the STM32CubeProgrammer log.
- Confirm the board was programmed in development boot mode and then rebooted in flash boot mode.
- Make sure the NUCLEO external loader, not the DK external loader, was selected.

If Windows Device Manager shows the USB camera but the Camera app opens the PC camera:
- Use the Camera app's switch-camera button to cycle between camera devices.
- Close and reopen the Camera app after connecting CN8.
- Check Windows privacy settings to make sure desktop apps can access cameras.
- Try OBS, VLC, or another camera viewer that lets you explicitly select the USB camera device.
- Temporarily disable the built-in PC camera in Device Manager if Windows keeps choosing it first.

If the webcam appears but the image is black:
- Re-check the B-CAMS-IMX FFC orientation.
- Re-seat the camera cable with the board unpowered.
- Verify the camera module is fully inserted into CN6.
- Look for serial logs showing sensor probe failure.

## References

- [NUCLEO-N657X0-Q product page - STMicroelectronics](https://www.st.com/en/evaluation-tools/nucleo-n657x0-q.html)
- [NUCLEO-N657X0-Q user manual - STMicroelectronics](https://www.st.com/resource/en/user_manual/um3417-stm32n6-nucleo144-board-mb1940-stmicroelectronics.pdf)
- [B-CAMS-IMX user manual - STMicroelectronics](https://www.st.com/resource/en/user_manual/um3354-camera-module-for-stm32-boards-stmicroelectronics.pdf)
- [x-cube-n6-camera-capture - STMicroelectronics GitHub](https://github.com/STMicroelectronics/x-cube-n6-camera-capture)
