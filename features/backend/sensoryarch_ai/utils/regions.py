from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class Region:
    bbox: tuple[int, int, int, int]  # x, y, w, h
    severity: float  # 0..1


def _bbox_from_contour(*, contour: np.ndarray) -> tuple[int, int, int, int]:
    x, y, w, h = cv2.boundingRect(contour)
    return int(x), int(y), int(w), int(h)


def extract_regions(
    *,
    layer_0_1: np.ndarray,
    threshold: float,
    min_area_px: int,
    max_regions: int,
) -> list[Region]:
    if layer_0_1 is None or layer_0_1.size == 0:
        return []
    if max_regions <= 0:
        return []

    layer = layer_0_1.astype(np.float32).clip(0.0, 1.0)
    mask = (layer >= float(threshold)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions: list[Region] = []
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < float(min_area_px):
            continue
        x, y, w, h = _bbox_from_contour(contour=contour)
        roi = layer[y : y + h, x : x + w]
        severity = float(np.mean(roi)) if roi.size else 0.0
        regions.append(Region(bbox=(x, y, w, h), severity=max(0.0, min(1.0, severity))))

    regions.sort(key=lambda r: r.severity, reverse=True)
    return regions[: max_regions]

