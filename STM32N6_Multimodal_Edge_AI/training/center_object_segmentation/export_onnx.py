"""Export a trained center-object segmentation checkpoint to ONNX."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from segmentation_model import CenterObjectResUNet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export center-object segmentation model.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--base-channels", type=int, default=32)
    parser.add_argument("--opset", type=int, default=17)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    saved_args = checkpoint.get("args", {})
    base_channels = int(saved_args.get("base_channels", args.base_channels))

    model = CenterObjectResUNet(base_channels=base_channels)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    dummy = torch.randn(1, 3, args.image_size, args.image_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    torch.onnx.export(
        model,
        dummy,
        args.output,
        input_names=["image"],
        output_names=["mask_logits"],
        opset_version=args.opset,
        dynamic_axes=None,
    )
    print(f"Exported {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
