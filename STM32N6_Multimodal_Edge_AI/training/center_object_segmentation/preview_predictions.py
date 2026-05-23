"""Save visual previews of model predictions on a dataset split."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw

from segmentation_model import CenterObjectResUNet


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview segmentation predictions.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--split", choices=("train", "val"), default="val")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=160)
    parser.add_argument("--base-channels", type=int, default=32)
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def load_model(checkpoint_path: Path, base_channels: int):
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    saved_args = checkpoint.get("args", {})
    base_channels = int(saved_args.get("base_channels", base_channels))

    model = CenterObjectResUNet(base_channels=base_channels)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model


def image_paths(data_root: Path, split: str):
    image_dir = data_root / "images" / split
    return [
        path
        for path in sorted(image_dir.iterdir())
        if path.suffix.lower() in IMAGE_EXTS
    ]


def tensor_from_image(image: Image.Image, image_size: int):
    resized = image.resize((image_size, image_size), Image.BILINEAR)
    array = np.asarray(resized, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)
    return tensor


def mask_image(mask_path: Path, size: tuple[int, int]):
    mask = Image.open(mask_path).convert("L")
    return mask.resize(size, Image.NEAREST)


def prediction_mask(model, image: Image.Image, image_size: int, threshold: float):
    with torch.no_grad():
        logits = model(tensor_from_image(image, image_size))
        probs = torch.sigmoid(logits)[0, 0].cpu().numpy()
    pred = (probs > threshold).astype(np.uint8) * 255
    return Image.fromarray(pred, mode="L").resize(image.size, Image.NEAREST)


def outline_overlay(image: Image.Image, gt_mask: Image.Image, pred_mask: Image.Image):
    canvas = image.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    gt_edges = mask_edges(np.asarray(gt_mask))
    pred_edges = mask_edges(np.asarray(pred_mask))

    gt_points = np.argwhere(gt_edges > 0)
    pred_points = np.argwhere(pred_edges > 0)

    for y, x in gt_points:
        draw.point((int(x), int(y)), fill=(0, 120, 255))
    for y, x in pred_points:
        draw.point((int(x), int(y)), fill=(0, 255, 80))

    return canvas


def mask_edges(mask: np.ndarray):
    binary = mask > 127
    padded = np.pad(binary, 1, mode="constant")
    center = padded[1:-1, 1:-1]
    neighbors = (
        padded[:-2, 1:-1]
        & padded[2:, 1:-1]
        & padded[1:-1, :-2]
        & padded[1:-1, 2:]
    )
    return np.where(center & ~neighbors, 255, 0).astype(np.uint8)


def concat_preview(image: Image.Image, gt_mask: Image.Image, pred_mask: Image.Image):
    overlay = outline_overlay(image, gt_mask, pred_mask)
    width, height = image.size
    canvas = Image.new("RGB", (width * 4, height), "black")
    canvas.paste(image.convert("RGB"), (0, 0))
    canvas.paste(gt_mask.convert("RGB"), (width, 0))
    canvas.paste(pred_mask.convert("RGB"), (width * 2, 0))
    canvas.paste(overlay, (width * 3, 0))
    return canvas


def main() -> int:
    args = parse_args()
    model = load_model(args.checkpoint, args.base_channels)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for image_path in image_paths(args.data_root, args.split):
        mask_path = args.data_root / "masks" / args.split / image_path.name
        if not mask_path.exists():
            print(f"missing mask for {image_path.name}")
            continue

        image = Image.open(image_path).convert("RGB")
        gt_mask = mask_image(mask_path, image.size)
        pred_mask = prediction_mask(model, image, args.image_size, args.threshold)
        preview = concat_preview(image, gt_mask, pred_mask)
        output_path = args.output_dir / f"preview_{image_path.name}"
        preview.save(output_path)
        print(f"saved {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
