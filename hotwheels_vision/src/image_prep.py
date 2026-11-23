"""Basic image preparation helpers for the Hot Wheels vision prototype.

This module deliberately does not claim to classify STH/Chase variants.
"""
from pathlib import Path
from typing import Tuple

import cv2


def load_image(path: str):
    """Load an image from disk; raise a useful error if it cannot be decoded."""
    image = cv2.imread(str(Path(path)))
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def crop_region(image, box: Tuple[int, int, int, int]):
    """Crop an (x1, y1, x2, y2) region after validating image bounds."""
    height, width = image.shape[:2]
    x1, y1, x2, y2 = map(int, box)
    if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
        raise ValueError("Crop box is outside image bounds or has zero area")
    return image[y1:y2, x1:x2].copy()


def prepare_for_ocr(image, scale: int = 3):
    """Enlarge and threshold a crop to make small printed marks easier to inspect.

    OCR itself is intentionally left to a later integration.
    """
    if scale < 1:
        raise ValueError("scale must be >= 1")
    enlarged = cv2.resize(
        image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
    )
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
