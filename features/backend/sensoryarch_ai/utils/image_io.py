from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Final

import cv2
import numpy as np


ALLOWED_EXTENSIONS: Final[set[str]] = {"jpg", "jpeg", "png"}


class InvalidImageError(ValueError):
    pass


@dataclass(frozen=True)
class DecodeImageResult:
    bgr: np.ndarray


def decode_image_bytes(*, image_bytes: bytes) -> DecodeImageResult:
    if not image_bytes:
        raise InvalidImageError("empty_upload")

    np_bytes = np.frombuffer(image_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
    if bgr is None or bgr.size == 0:
        raise InvalidImageError("decode_failed")

    return DecodeImageResult(bgr=bgr)


def resize_to_max_side(*, bgr: np.ndarray, max_side_px: int) -> np.ndarray:
    if bgr is None or bgr.size == 0:
        raise InvalidImageError("empty_image_array")
    if max_side_px <= 0:
        return bgr

    height, width = bgr.shape[:2]
    max_side = max(height, width)
    if max_side <= max_side_px:
        return bgr

    scale = max_side_px / float(max_side)
    new_w = max(1, int(round(width * scale)))
    new_h = max(1, int(round(height * scale)))
    return cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def encode_png_data_url(*, bgr_or_bgra: np.ndarray) -> str:
    if bgr_or_bgra is None or bgr_or_bgra.size == 0:
        raise InvalidImageError("empty_image_array")

    ok, png = cv2.imencode(".png", bgr_or_bgra)
    if not ok:
        raise InvalidImageError("png_encode_failed")

    b64 = base64.b64encode(png.tobytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"

