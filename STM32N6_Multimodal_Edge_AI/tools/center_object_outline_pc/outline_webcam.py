"""PC-side prototype for outlining the object near the center of a webcam frame."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError as exc:
    missing = exc.name or "opencv-python"
    print(
        f"Missing dependency: {missing}\n"
        "Install dependencies with:\n"
        "  python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


WINDOW_NAME = "STM32N6 center-object outline"
METHODS = ("background", "color", "grabcut", "edges")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Outline the dominant object near the center of a webcam frame."
    )
    parser.add_argument("--camera-index", type=int, default=0, help="OpenCV camera index.")
    parser.add_argument("--width", type=int, default=800, help="Requested capture width.")
    parser.add_argument("--height", type=int, default=480, help="Requested capture height.")
    parser.add_argument("--fps", type=int, default=30, help="Requested capture FPS.")
    parser.add_argument(
        "--fourcc",
        default="",
        help="Optional capture FourCC, for example YUY2 or MJPG.",
    )
    parser.add_argument(
        "--process-scale",
        type=float,
        default=0.5,
        help="Scale factor for processing. Lower is faster; display stays full size.",
    )
    parser.add_argument(
        "--process-every",
        type=int,
        default=1,
        help="Run segmentation every N frames and reuse the last outline between updates.",
    )
    parser.add_argument(
        "--method",
        choices=METHODS,
        default="background",
        help="Foreground extraction method.",
    )
    parser.add_argument(
        "--center-width",
        type=float,
        default=0.55,
        help="Centered ROI width as a fraction of frame width.",
    )
    parser.add_argument(
        "--center-height",
        type=float,
        default=0.70,
        help="Centered ROI height as a fraction of frame height.",
    )
    parser.add_argument("--min-area", type=int, default=900, help="Minimum contour area.")
    parser.add_argument(
        "--diff-threshold",
        type=int,
        default=28,
        help="Background-mode Lab distance threshold.",
    )
    parser.add_argument(
        "--color-threshold",
        type=int,
        default=32,
        help="Color-mode Lab distance threshold from the center patch.",
    )
    parser.add_argument(
        "--center-sample",
        type=int,
        default=28,
        help="Color-mode center patch size in pixels.",
    )
    parser.add_argument(
        "--grabcut-iters", type=int, default=2, help="GrabCut iterations per frame."
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=None,
        help="Directory for frames saved with the s key.",
    )
    return parser.parse_args()


def clamp_fraction(value: float, fallback: float) -> float:
    if value <= 0.05 or value >= 0.98:
        return fallback
    return value


def center_rect(frame_shape: tuple[int, int, int], width_frac: float, height_frac: float):
    height, width = frame_shape[:2]
    rect_w = int(width * clamp_fraction(width_frac, 0.55))
    rect_h = int(height * clamp_fraction(height_frac, 0.70))
    x = max(1, (width - rect_w) // 2)
    y = max(1, (height - rect_h) // 2)
    rect_w = min(rect_w, width - x - 1)
    rect_h = min(rect_h, height - y - 1)
    return x, y, rect_w, rect_h


def processing_frame(frame, scale: float):
    if scale >= 0.999:
        return frame
    scale = max(0.1, min(scale, 1.0))
    width = max(32, int(frame.shape[1] * scale))
    height = max(32, int(frame.shape[0] * scale))
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)


def scale_rect(rect, x_scale: float, y_scale: float):
    x, y, w, h = rect
    return (
        int(x * x_scale),
        int(y * y_scale),
        int(w * x_scale),
        int(h * y_scale),
    )


def scale_contour(contour, x_scale: float, y_scale: float):
    if contour is None:
        return None
    scaled = contour.astype(np.float32)
    scaled[:, :, 0] *= x_scale
    scaled[:, :, 1] *= y_scale
    return scaled.astype(np.int32)


def roi_mask(frame_shape: tuple[int, int, int], rect):
    mask = np.zeros(frame_shape[:2], dtype=np.uint8)
    x, y, w, h = rect
    mask[y : y + h, x : x + w] = 255
    return mask


def background_mask(frame, background, args: argparse.Namespace):
    rect = center_rect(frame.shape, args.center_width, args.center_height)
    if background is None:
        return np.zeros(frame.shape[:2], dtype=np.uint8), rect, "press b with empty background"

    frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
    bg_blur = cv2.GaussianBlur(background, (5, 5), 0)
    frame_lab = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2LAB).astype(np.float32)
    bg_lab = cv2.cvtColor(bg_blur, cv2.COLOR_BGR2LAB).astype(np.float32)
    distance = np.linalg.norm(frame_lab - bg_lab, axis=2)
    mask = np.where(distance > args.diff_threshold, 255, 0).astype(np.uint8)
    mask = cv2.bitwise_and(mask, roi_mask(frame.shape, rect))
    return cleanup_mask(mask), rect, "background locked"


def color_mask(frame, args: argparse.Namespace):
    rect = center_rect(frame.shape, args.center_width, args.center_height)
    height, width = frame.shape[:2]
    half = max(4, args.center_sample // 2)
    cx = width // 2
    cy = height // 2
    x0 = max(0, cx - half)
    x1 = min(width, cx + half)
    y0 = max(0, cy - half)
    y1 = min(height, cy + half)

    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
    center_patch = lab[y0:y1, x0:x1]
    center_color = np.median(center_patch.reshape(-1, 3), axis=0)
    distance = np.linalg.norm(lab - center_color, axis=2)
    mask = np.where(distance < args.color_threshold, 255, 0).astype(np.uint8)
    mask = cv2.bitwise_and(mask, roi_mask(frame.shape, rect))
    return cleanup_mask(mask), rect, "center color"


def grabcut_mask(frame, args: argparse.Namespace):
    rect = center_rect(frame.shape, args.center_width, args.center_height)
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    bg_model = np.zeros((1, 65), dtype=np.float64)
    fg_model = np.zeros((1, 65), dtype=np.float64)

    try:
        cv2.grabCut(
            frame,
            mask,
            rect,
            bg_model,
            fg_model,
            args.grabcut_iters,
            cv2.GC_INIT_WITH_RECT,
        )
    except cv2.error:
        return np.zeros(frame.shape[:2], dtype=np.uint8), rect, "grabcut failed"

    foreground = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)
    return cleanup_mask(foreground), rect, "grabcut"


def edges_mask(frame, args: argparse.Namespace):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 45, 130)
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.dilate(edges, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return cleanup_mask(mask), center_rect(frame.shape, args.center_width, args.center_height), "edges"


def cleanup_mask(mask):
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask


def component_nearest_center(mask, min_area: int):
    height, width = mask.shape[:2]
    frame_center = np.array([width / 2.0, height / 2.0])
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)

    best_label = None
    best_score = -1.0
    max_distance = float(np.linalg.norm(frame_center))

    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < min_area:
            continue

        centroid = centroids[label]
        distance = float(np.linalg.norm(centroid - frame_center))
        center_score = 1.0 - min(distance / max_distance, 1.0)
        score = (area**0.5) * (0.35 + center_score)

        if score > best_score:
            best_score = score
            best_label = label

    if best_label is None:
        return None

    return np.where(labels == best_label, 255, 0).astype(np.uint8)


def outline_from_mask(mask, min_area: int):
    component = component_nearest_center(mask, min_area)
    if component is None:
        return None

    contours, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [contour for contour in contours if cv2.contourArea(contour) >= min_area]
    if not contours:
        return None

    return max(contours, key=cv2.contourArea)


def draw_overlay(frame, contour, rect, method: str, fps: float, status: str):
    overlay = frame.copy()
    x, y, w, h = rect
    height, width = frame.shape[:2]
    center = (width // 2, height // 2)

    cv2.rectangle(overlay, (x, y), (x + w, y + h), (70, 120, 255), 1)
    cv2.drawMarker(overlay, center, (70, 120, 255), cv2.MARKER_CROSS, 18, 1)

    if contour is not None:
        cv2.drawContours(overlay, [contour], -1, (0, 255, 80), 3)
        area = int(cv2.contourArea(contour))
        cv2.putText(
            overlay,
            f"outline area: {area}",
            (12, height - 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 80),
            2,
            cv2.LINE_AA,
        )
    else:
        cv2.putText(
            overlay,
            "no centered object",
            (12, height - 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 180, 255),
            2,
            cv2.LINE_AA,
        )

    top_line = f"{method} | {fps:4.1f} fps | b background | m method | s save | q quit"
    cv2.putText(overlay, top_line, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(overlay, status, (12, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)
    return overlay


def open_camera(index: int, width: int, height: int, fps: int, fourcc: str):
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not capture.isOpened():
        capture = cv2.VideoCapture(index)

    if not capture.isOpened():
        raise RuntimeError(f"Could not open camera index {index}")

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if len(fourcc) == 4:
        capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc[:4]))
    return capture


def save_frame(save_dir: Path, raw_frame, annotated_frame):
    save_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    raw_path = save_dir / f"raw_{stamp}.png"
    annotated_path = save_dir / f"outline_{stamp}.png"
    cv2.imwrite(str(raw_path), raw_frame)
    cv2.imwrite(str(annotated_path), annotated_frame)
    print(f"Saved {raw_path}")
    print(f"Saved {annotated_path}")


def main() -> int:
    args = parse_args()
    if args.save_dir is None:
        args.save_dir = Path(__file__).resolve().parents[2] / "data" / "samples" / "camera"

    method_index = METHODS.index(args.method)
    capture = open_camera(args.camera_index, args.width, args.height, args.fps, args.fourcc)
    print(f"Opened camera index {args.camera_index}")

    last_time = time.perf_counter()
    fps = 0.0
    background = None
    flash_message = ""
    flash_until = 0.0
    frame_count = 0
    last_contour = None
    last_rect = None
    last_status = "starting"

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Camera frame read failed", file=sys.stderr)
                return 2

            frame_count += 1
            method = METHODS[method_index]
            process_now = frame_count % max(args.process_every, 1) == 0

            if process_now or last_rect is None:
                work_frame = processing_frame(frame, args.process_scale)
                work_background = (
                    processing_frame(background, args.process_scale)
                    if background is not None
                    else None
                )

                if method == "background":
                    mask, rect, status = background_mask(work_frame, work_background, args)
                elif method == "color":
                    mask, rect, status = color_mask(work_frame, args)
                elif method == "grabcut":
                    mask, rect, status = grabcut_mask(work_frame, args)
                else:
                    mask, rect, status = edges_mask(work_frame, args)

                contour = outline_from_mask(mask, args.min_area)
                x_scale = frame.shape[1] / work_frame.shape[1]
                y_scale = frame.shape[0] / work_frame.shape[0]
                last_contour = scale_contour(contour, x_scale, y_scale)
                last_rect = scale_rect(rect, x_scale, y_scale)
                last_status = f"{status} | process {work_frame.shape[1]}x{work_frame.shape[0]}"

            now = time.perf_counter()
            elapsed = max(now - last_time, 1e-6)
            last_time = now
            fps = (fps * 0.85) + ((1.0 / elapsed) * 0.15)

            if flash_message and time.perf_counter() < flash_until:
                status = flash_message
            else:
                status = last_status

            output = draw_overlay(frame, last_contour, last_rect, method, fps, status)
            cv2.imshow(WINDOW_NAME, output)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                save_frame(args.save_dir, frame, output)
            if key == ord("m"):
                method_index = (method_index + 1) % len(METHODS)
                last_rect = None
                last_contour = None
            if key == ord("r"):
                background = None
                last_time = time.perf_counter()
                last_rect = None
                last_contour = None
                flash_message = "reset"
                flash_until = time.perf_counter() + 1.0
            if key == ord("b"):
                background = frame.copy()
                last_rect = None
                last_contour = None
                flash_message = "captured background"
                flash_until = time.perf_counter() + 1.0

    finally:
        capture.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
