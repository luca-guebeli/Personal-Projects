# Center-Object Segmentation Training

This is the PC-side training pipeline for the center-object outline model.

The first model is intentionally stronger than the final embedded target: a residual U-Net-style binary segmentation network. It should help prove the dataset, labels, and preprocessing before building a smaller STM32N6 deployment model.

## Dataset

Expected dataset path:

```text
../../data/segmentation/
|-- images/
|   |-- train/
|   `-- val/
`-- masks/
    |-- train/
    `-- val/
```

Every image must have a mask with the same filename.

## Label Masks

Use the simple polygon labeler on raw frames saved from the webcam prototype:

```powershell
python label_masks.py --input-dir ..\..\data\samples\camera --output-root ..\..\data\segmentation --split train
```

Label most images as `train`, then label a smaller set as `val`:

```powershell
python label_masks.py --input-dir ..\..\data\samples\camera --output-root ..\..\data\segmentation --split val
```

Controls:

- left click: add polygon point
- `u`: undo last point
- `c`: clear points
- `e`: save empty mask
- `Enter` or `Space`: save polygon mask
- `n`: skip image
- `q`: quit

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For GPU training, install the PyTorch build that matches your CUDA setup from the official PyTorch selector.

On this machine, prefer the standard Windows CPython environment:

```powershell
C:\Users\lucag\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install -r requirements.txt
```

The default `python` currently points to MSYS2/UCRT Python, which does not match normal PyTorch Windows wheels.

## Train

```powershell
python train.py --data-root ..\..\data\segmentation --epochs 50 --batch-size 8 --image-size 256
```

Useful quick smoke test:

```powershell
python train.py --data-root ..\..\data\segmentation --epochs 1 --batch-size 2 --image-size 160
```

Outputs go to `runs/center_object_resunet/` and are ignored by Git.

First baseline notes are tracked in [results.md](results.md).

## Preview Predictions

After training, save validation previews:

```powershell
python preview_predictions.py --checkpoint runs\center_object_resunet_160\best.pt --data-root ..\..\data\segmentation --split val --output-dir runs\center_object_resunet_160\previews --image-size 160
```

Each preview is four panels:

- original image
- ground-truth mask
- predicted mask
- overlay with ground truth in blue and prediction in green

## Export To ONNX

```powershell
python export_onnx.py --checkpoint runs\center_object_resunet\best.pt --output runs\center_object_resunet\center_object_resunet.onnx --image-size 256
```

The ONNX file is a PC interchange artifact. It is not yet the final STM32N6 deployment model.

## Training Notes

- Use masks that label only the object you want outlined.
- Include empty-background images with empty masks.
- Include low-contrast objects; those are exactly where the classical baseline struggled.
- Save a few bad examples from the webcam prototype and label them first.
- Once this model works, use it to guide a smaller 160x160 or 224x224 model for STM32N6.
