# Firmware Workspace

Firmware for the STM32N6 board will live here once the exact board and starting example are chosen.

## Intended Structure

```text
firmware/
|-- README.md
|-- board/
|   `-- README.md
|-- app/
|   `-- README.md
|-- drivers/
|   `-- README.md
`-- middleware/
    `-- README.md
```

## Starting Approach

- Start from the closest official STM32CubeN6 board example.
- Keep generated code separate from application code where practical.
- Add one hardware feature at a time: logging, camera, audio, then AI inference.
- Record exact Cube package versions and IDE versions in this README once selected.

## Things To Track

- Board support package used
- STM32CubeN6 version
- Toolchain and compiler version
- Flash/debug workflow
- Memory map and external memory configuration
- Camera buffer format and placement
- Audio DMA buffer format and placement
- AI runtime and model integration path
