"""Simple polygon mask labeler for center-object segmentation frames."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
WINDOW_NAME = "center-object mask labeler"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create binary segmentation masks.")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--split", choices=("train", "val"), default="train")
    return parser.parse_args()


class LabelState:
    def __init__(self):
        self.points: list[tuple[int, int]] = []

    def mouse(self, event, x, y, _flags, _userdata):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))


def image_paths(input_dir: Path):
    return [
        path
        for path in sorted(input_dir.iterdir())
        if path.suffix.lower() in IMAGE_EXTS and not path.name.startswith("outline_")
    ]


def draw_preview(image, points):
    preview = image.copy()
    if points:
        for point in points:
            cv2.circle(preview, point, 4, (0, 255, 255), -1)
        for start, end in zip(points, points[1:]):
            cv2.line(preview, start, end, (0, 255, 255), 2)
        if len(points) >= 3:
            cv2.line(preview, points[-1], points[0], (0, 180, 255), 1)

    cv2.putText(
        preview,
        "click polygon | enter save | e empty | u undo | c clear | n skip | q quit",
        (12, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return preview


def save_pair(image_path: Path, image, points, output_root: Path, split: str):
    image_dir = output_root / "images" / split
    mask_dir = output_root / "masks" / split
    image_dir.mkdir(parents=True, exist_ok=True)
    mask_dir.mkdir(parents=True, exist_ok=True)

    out_image = image_dir / image_path.name
    out_mask = mask_dir / image_path.name

    if image_path.resolve() != out_image.resolve():
        shutil.copy2(image_path, out_image)

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    if len(points) >= 3:
        polygon = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [polygon], 255)

    cv2.imwrite(str(out_mask), mask)
    print(f"saved {out_image}")
    print(f"saved {out_mask}")


def main() -> int:
    args = parse_args()
    paths = image_paths(args.input_dir)
    if not paths:
        raise RuntimeError(f"No images found in {args.input_dir}")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    for index, path in enumerate(paths, start=1):
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            print(f"skipping unreadable image: {path}")
            continue

        state = LabelState()
        cv2.setMouseCallback(WINDOW_NAME, state.mouse)

        while True:
            preview = draw_preview(image, state.points)
            cv2.putText(
                preview,
                f"{index}/{len(paths)} {path.name}",
                (12, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(WINDOW_NAME, preview)
            key = cv2.waitKey(20) & 0xFF

            if key == ord("q"):
                cv2.destroyAllWindows()
                return 0
            if key == ord("n"):
                break
            if key == ord("u") and state.points:
                state.points.pop()
            if key == ord("c"):
                state.points.clear()
            if key == ord("e"):
                save_pair(path, image, [], args.output_root, args.split)
                break
            if key in (13, 32):
                if len(state.points) < 3:
                    print("need at least 3 points, or press e for an empty mask")
                    continue
                save_pair(path, image, state.points, args.output_root, args.split)
                break

    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
