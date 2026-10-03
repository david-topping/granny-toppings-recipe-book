from pathlib import Path

import cv2
import numpy as np

from toppings.recipe import PROCESSED, scan_images

MAX_EDGE = 1500


def find_card(image: np.ndarray) -> np.ndarray | None:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 30, 100)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    image_area = image.shape[0] * image.shape[1]
    if not 0.25 < cv2.contourArea(largest) / image_area < 0.98:
        return None
    approx = cv2.approxPolyDP(largest, 0.02 * cv2.arcLength(largest, True), True)
    if len(approx) == 4:
        return approx.reshape(4, 2).astype(np.float32)
    return cv2.boxPoints(cv2.minAreaRect(largest)).astype(np.float32)


def order_corners(pts: np.ndarray) -> np.ndarray:
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], np.float32)


def crop_to_card(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    tl, tr, br, bl = order_corners(corners)
    width = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    height = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    target = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], np.float32)
    matrix = cv2.getPerspectiveTransform(np.array([tl, tr, br, bl]), target)
    return cv2.warpPerspective(image, matrix, (width, height))


def normalise_contrast(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, a, b = cv2.split(lab)
    lightness = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lightness)
    return cv2.cvtColor(cv2.merge([lightness, a, b]), cv2.COLOR_LAB2BGR)


def resize(image: np.ndarray) -> np.ndarray:
    scale = MAX_EDGE / max(image.shape[:2])
    if scale >= 1:
        return image
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def preprocess_image(src: Path, dest: Path) -> bool:
    # 1. Load image
    image = cv2.imread(str(src))
    if image is None:
        return False

    # 2. Deskew and crop to the card
    corners = find_card(image)
    if corners is not None:
        image = crop_to_card(image, corners)

    # 3. Normalise contrast and resize
    image = resize(normalise_contrast(image))
    cv2.imwrite(str(dest), image, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return True


def run() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    for src in scan_images():
        dest = PROCESSED / f"{src.stem}.jpg"
        if dest.exists():
            print(f"skip {src.name} (already processed)")
        elif preprocess_image(src, dest):
            print(f"processed {src.name} -> {dest}")
        else:
            print(f"could not read {src.name}")
