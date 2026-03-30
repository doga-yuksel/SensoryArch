from __future__ import annotations

import cv2
import numpy as np


def render_heatmap_overlay(*, bgr: np.ndarray, heat_0_1: np.ndarray, alpha: float) -> np.ndarray:
    if bgr is None or bgr.size == 0:
        raise ValueError("empty_image")
    if heat_0_1 is None or heat_0_1.size == 0:
        raise ValueError("empty_heatmap")

    heat = (heat_0_1.astype(np.float32).clip(0.0, 1.0) * 255.0).astype(np.uint8)
    heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    alpha_f = float(alpha)
    alpha_f = max(0.0, min(1.0, alpha_f))
    overlay = cv2.addWeighted(bgr, 1.0 - alpha_f, heat_color, alpha_f, 0.0)
    return overlay

