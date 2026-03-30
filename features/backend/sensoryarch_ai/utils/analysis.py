from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class RiskLayers:
    light: np.ndarray  # float32 0..1
    reflection: np.ndarray  # float32 0..1
    pattern: np.ndarray  # float32 0..1
    combined: np.ndarray  # float32 0..1


def _normalize_0_1(*, img: np.ndarray) -> np.ndarray:
    if img.dtype != np.float32:
        img = img.astype(np.float32)
    min_v = float(np.min(img))
    max_v = float(np.max(img))
    if max_v <= min_v + 1e-6:
        return np.zeros_like(img, dtype=np.float32)
    return (img - min_v) / (max_v - min_v)


def compute_light_layer(*, bgr: np.ndarray, v_threshold: int) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    mask = (v >= int(v_threshold)).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 5)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return (mask.astype(np.float32) / 255.0).clip(0.0, 1.0)


def compute_reflection_layer(*, bgr: np.ndarray, v_threshold: int, s_threshold: int) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    mask = ((v >= int(v_threshold)) & (s <= int(s_threshold))).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 5)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return (mask.astype(np.float32) / 255.0).clip(0.0, 1.0)


def compute_pattern_layer(*, bgr: np.ndarray, edge_density_scale: float) -> np.ndarray:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    edges_f = edges.astype(np.float32) / 255.0
    kernel = (15, 15)
    density = cv2.blur(edges_f, kernel)
    density = (density * float(edge_density_scale)).clip(0.0, 1.0)
    return density.astype(np.float32)


def combine_layers(*, light: np.ndarray, reflection: np.ndarray, pattern: np.ndarray, weights: tuple[float, float, float]) -> np.ndarray:
    w1, w2, w3 = weights
    combined = (w1 * light) + (w2 * reflection) + (w3 * pattern)
    return _normalize_0_1(img=combined).astype(np.float32)


def analyze_image(
    *,
    bgr: np.ndarray,
    v_threshold: int,
    s_threshold: int,
    edge_density_scale: float,
    weights: tuple[float, float, float],
) -> RiskLayers:
    light = compute_light_layer(bgr=bgr, v_threshold=v_threshold)
    reflection = compute_reflection_layer(bgr=bgr, v_threshold=v_threshold, s_threshold=s_threshold)
    pattern = compute_pattern_layer(bgr=bgr, edge_density_scale=edge_density_scale)
    combined = combine_layers(light=light, reflection=reflection, pattern=pattern, weights=weights)
    return RiskLayers(light=light, reflection=reflection, pattern=pattern, combined=combined)

