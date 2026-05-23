# Segmentation Dataset

This folder is for paired camera frames and binary masks used to train the center-object outline model.

## Expected Layout

```text
data/segmentation/
|-- images/
|   |-- train/
|   `-- val/
`-- masks/
    |-- train/
    `-- val/
```

Each image must have a mask with the same filename:

```text
images/train/frame_0001.png
masks/train/frame_0001.png
```

## Mask Format

- Black pixels: background
- White pixels: object to outline
- File format: PNG preferred
- Keep masks single-channel if possible

## First Dataset Target

Start narrow:

- centered desk objects
- electronics parts
- hands holding objects
- empty background frames
- different distances
- different lighting
- difficult low-contrast examples

Aim for 100 to 300 labeled frames before judging the first model seriously.
