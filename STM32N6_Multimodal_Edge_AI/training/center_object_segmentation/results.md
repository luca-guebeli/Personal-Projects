# Training Results

## Baseline 001: ResUNet 160

Command:

```powershell
.\.venv-win\Scripts\python.exe train.py --data-root ..\..\data\segmentation --epochs 5 --batch-size 4 --image-size 160 --output-dir runs\center_object_resunet_160
```

Dataset:

- Train: 33 image/mask pairs
- Validation: 8 image/mask pairs
- Average foreground coverage: about 6% to 7% of each frame

Result:

- Epochs: 5
- Device: CPU
- Parameters: 6,420,273
- Best validation IoU: 0.3588
- Best validation Dice: 0.4689
- Best checkpoint: `runs/center_object_resunet_160/best.pt`
- Validation previews: `runs/center_object_resunet_160/previews/`

Observations:

- The training loop and dataset format work.
- The model starts learning foreground structure within 5 CPU epochs.
- Early previews show that the model can pick up salient objects, but it does not yet consistently match the full intended object mask.
- More labeled samples and longer training are needed before judging architecture quality.

Next:

- Add more labeled images with consistent mask policy.
- Include harder low-contrast examples.
- Train 20 to 50 epochs at 160 or 256 input size.
- Preview validation predictions after each serious run.
