"""Train a binary center-object segmentation model."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageEnhance, ImageOps
from torch import nn
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from segmentation_model import CenterObjectResUNet, count_parameters


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class Sample:
    image_path: Path
    mask_path: Path


class SegmentationDataset(Dataset):
    def __init__(self, data_root: Path, split: str, image_size: int, augment: bool):
        self.data_root = data_root
        self.split = split
        self.image_size = image_size
        self.augment = augment
        self.samples = self._load_samples()

        if not self.samples:
            raise RuntimeError(f"No samples found for split '{split}' under {data_root}")

    def _load_samples(self) -> list[Sample]:
        image_dir = self.data_root / "images" / self.split
        mask_dir = self.data_root / "masks" / self.split

        if not image_dir.exists():
            raise RuntimeError(f"Missing image directory: {image_dir}")
        if not mask_dir.exists():
            raise RuntimeError(f"Missing mask directory: {mask_dir}")

        samples: list[Sample] = []
        for image_path in sorted(image_dir.iterdir()):
            if image_path.suffix.lower() not in IMAGE_EXTS:
                continue
            mask_path = mask_dir / image_path.name
            if not mask_path.exists():
                raise RuntimeError(f"Missing mask for {image_path.name}: {mask_path}")
            samples.append(Sample(image_path=image_path, mask_path=mask_path))
        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        sample = self.samples[index]
        image = Image.open(sample.image_path).convert("RGB")
        mask = Image.open(sample.mask_path).convert("L")

        image = image.resize((self.image_size, self.image_size), Image.BILINEAR)
        mask = mask.resize((self.image_size, self.image_size), Image.NEAREST)

        if self.augment:
            image, mask = augment_pair(image, mask)

        image_array = np.asarray(image, dtype=np.float32) / 255.0
        mask_array = (np.asarray(mask, dtype=np.float32) > 127).astype(np.float32)

        image_tensor = torch.from_numpy(image_array).permute(2, 0, 1)
        mask_tensor = torch.from_numpy(mask_array).unsqueeze(0)
        return image_tensor, mask_tensor


def augment_pair(image: Image.Image, mask: Image.Image):
    if random.random() < 0.5:
        image = ImageOps.mirror(image)
        mask = ImageOps.mirror(mask)

    if random.random() < 0.20:
        image = ImageOps.flip(image)
        mask = ImageOps.flip(mask)

    if random.random() < 0.7:
        image = ImageEnhance.Brightness(image).enhance(random.uniform(0.75, 1.25))
        image = ImageEnhance.Contrast(image).enhance(random.uniform(0.75, 1.35))
        image = ImageEnhance.Color(image).enhance(random.uniform(0.80, 1.25))

    return image, mask


def dice_loss(logits: torch.Tensor, targets: torch.Tensor, eps: float = 1e-6):
    probs = torch.sigmoid(logits)
    dims = (1, 2, 3)
    intersection = torch.sum(probs * targets, dims)
    cardinality = torch.sum(probs + targets, dims)
    dice = (2.0 * intersection + eps) / (cardinality + eps)
    return 1.0 - dice.mean()


def segmentation_loss(logits: torch.Tensor, targets: torch.Tensor):
    bce = nn.functional.binary_cross_entropy_with_logits(logits, targets)
    return bce + dice_loss(logits, targets)


@torch.no_grad()
def metrics_from_logits(logits: torch.Tensor, targets: torch.Tensor):
    probs = torch.sigmoid(logits)
    preds = (probs > 0.5).float()
    dims = (1, 2, 3)
    intersection = torch.sum(preds * targets, dims)
    union = torch.sum((preds + targets) > 0, dims).float()
    pred_sum = torch.sum(preds, dims)
    target_sum = torch.sum(targets, dims)

    iou = (intersection + 1e-6) / (union + 1e-6)
    dice = (2.0 * intersection + 1e-6) / (pred_sum + target_sum + 1e-6)
    return iou.mean().item(), dice.mean().item()


def run_epoch(model, loader, optimizer, device: torch.device, training: bool):
    model.train(training)
    total_loss = 0.0
    total_iou = 0.0
    total_dice = 0.0
    total_batches = 0

    label = "train" if training else "val"
    iterator = tqdm(loader, desc=label, leave=False)

    for images, masks in iterator:
        images = images.to(device)
        masks = masks.to(device)

        if training:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = segmentation_loss(logits, masks)
            if training:
                loss.backward()
                optimizer.step()

        iou, dice = metrics_from_logits(logits.detach(), masks)
        total_loss += loss.item()
        total_iou += iou
        total_dice += dice
        total_batches += 1
        iterator.set_postfix(loss=loss.item(), iou=iou, dice=dice)

    return {
        "loss": total_loss / max(total_batches, 1),
        "iou": total_iou / max(total_batches, 1),
        "dice": total_dice / max(total_batches, 1),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train center-object segmentation.")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("runs") / "center_object_resunet")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--base-channels", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def save_checkpoint(path: Path, model, optimizer, epoch: int, metrics: dict, args):
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "metrics": metrics,
            "args": vars(args),
        },
        path,
    )


def main() -> int:
    args = parse_args()
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    train_dataset = SegmentationDataset(args.data_root, "train", args.image_size, augment=True)
    val_dataset = SegmentationDataset(args.data_root, "val", args.image_size, augment=False)
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )

    model = CenterObjectResUNet(base_channels=args.base_channels).to(device)
    print(f"Trainable parameters: {count_parameters(model):,}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(args.epochs, 1))

    best_iou = -1.0
    for epoch in range(1, args.epochs + 1):
        train_metrics = run_epoch(model, train_loader, optimizer, device, training=True)
        val_metrics = run_epoch(model, val_loader, optimizer, device, training=False)
        scheduler.step()

        print(
            f"epoch {epoch:03d} | "
            f"train loss {train_metrics['loss']:.4f} iou {train_metrics['iou']:.4f} | "
            f"val loss {val_metrics['loss']:.4f} iou {val_metrics['iou']:.4f} "
            f"dice {val_metrics['dice']:.4f}"
        )

        save_checkpoint(args.output_dir / "last.pt", model, optimizer, epoch, val_metrics, args)
        if val_metrics["iou"] > best_iou:
            best_iou = val_metrics["iou"]
            save_checkpoint(args.output_dir / "best.pt", model, optimizer, epoch, val_metrics, args)
            print(f"saved best checkpoint with val IoU {best_iou:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
