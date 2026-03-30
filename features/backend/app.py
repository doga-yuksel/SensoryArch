from __future__ import annotations

import time
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

from sensoryarch_ai.types.models import AnalyzeResponse, Recommendation, RiskRegion
from sensoryarch_ai.types.settings import load_settings
from sensoryarch_ai.utils.analysis import analyze_image
from sensoryarch_ai.utils.heatmap import render_heatmap_overlay
from sensoryarch_ai.utils.image_io import InvalidImageError, decode_image_bytes, encode_png_data_url, resize_to_max_side
from sensoryarch_ai.utils.regions import extract_regions


APP_VERSION = "0.1.0"


def _json_error(*, code: str, message: str, http_status: int, details: dict[str, Any] | None = None):
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), int(http_status)


def create_app() -> Flask:
    settings = load_settings()

    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = int(settings.max_upload_mb) * 1024 * 1024

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.get("/version")
    def version():
        return jsonify({"version": APP_VERSION})

    @app.post("/analyze")
    def analyze():
        t0 = time.perf_counter()

        if "image" not in request.files:
            return _json_error(code="missing_image", message="Multipart field 'image' is required.", http_status=400)

        file = request.files["image"]
        if not file or not file.filename:
            return _json_error(code="empty_upload", message="No file uploaded.", http_status=400)

        try:
            image_bytes = file.read()
            decoded = decode_image_bytes(image_bytes=image_bytes)
            bgr = resize_to_max_side(bgr=decoded.bgr, max_side_px=settings.max_image_side_px)
        except InvalidImageError as exc:
            return _json_error(code="invalid_image", message="Invalid or unsupported image.", http_status=400, details={"reason": str(exc)})

        layers = analyze_image(
            bgr=bgr,
            v_threshold=settings.light_v_threshold,
            s_threshold=settings.reflection_s_threshold,
            edge_density_scale=settings.pattern_edge_density_scale,
            weights=(settings.light_weight, settings.reflection_weight, settings.pattern_weight),
        )

        overlay_bgr = render_heatmap_overlay(bgr=bgr, heat_0_1=layers.combined, alpha=0.45)
        heatmap_data_url = encode_png_data_url(bgr_or_bgra=overlay_bgr)

        risk_regions: list[RiskRegion] = []
        recommendations: list[Recommendation] = []

        def add_regions(*, layer_0_1, region_type: str, region_prefix: str):
            regions = extract_regions(layer_0_1=layer_0_1, threshold=0.65, min_area_px=800, max_regions=5)
            for idx, region in enumerate(regions, start=1):
                region_id = f"{region_prefix}{idx}"
                x, y, w, h = region.bbox
                risk_regions.append(
                    RiskRegion(
                        id=region_id,
                        type=region_type,  # type: ignore[arg-type]
                        severity=region.severity,
                        bbox={"x": x, "y": y, "w": w, "h": h},
                    )
                )

        add_regions(layer_0_1=layers.light, region_type="light", region_prefix="l")
        add_regions(layer_0_1=layers.reflection, region_type="reflection", region_prefix="rf")
        add_regions(layer_0_1=layers.pattern, region_type="pattern", region_prefix="p")

        def add_recommendations(*, region: RiskRegion):
            if region.type == "light":
                return Recommendation(
                    region_id=region.id,
                    title="Aydınlatmayı yumuşatın",
                    actions=[
                        "Difüzör veya opal kapak kullanın",
                        "Daha düşük parlaklık / daha homojen dağılım hedefleyin",
                        "Göz hizasında doğrudan ışık kaynağını azaltın",
                    ],
                )
            if region.type == "reflection":
                return Recommendation(
                    region_id=region.id,
                    title="Parlamayı azaltın",
                    actions=[
                        "Mat boya / yansımasız kaplama tercih edin",
                        "Parlak yüzey alanını azaltın (cam/metal/seramik)",
                        "Işık yönünü değiştirin (yansıma açısını kırın)",
                    ],
                )
            if region.type == "pattern":
                return Recommendation(
                    region_id=region.id,
                    title="Görsel paterni sadeleştirin",
                    actions=[
                        "Yüksek kontrastlı desenleri azaltın",
                        "Doku tekrarını düşürün (daha düz yüzeyler)",
                        "Renk paletini sakinleştirin (az sayıda ton)",
                    ],
                )
            return Recommendation(region_id=region.id, title="Genel iyileştirme", actions=["Uyaran yoğunluğunu azaltın"])

        for region in risk_regions:
            recommendations.append(add_recommendations(region=region))

        light_level = float(layers.light.mean())
        reflection_level = float(layers.reflection.mean())
        pattern_level = float(layers.pattern.mean())
        penalty = (settings.light_weight * light_level) + (settings.reflection_weight * reflection_level) + (settings.pattern_weight * pattern_level)
        score = int(round(max(0.0, min(100.0, 100.0 - (100.0 * penalty)))))

        timing_ms = int(round((time.perf_counter() - t0) * 1000.0))

        response = AnalyzeResponse(
            score=score,
            timing_ms=timing_ms,
            heatmap_image=heatmap_data_url,
            risk_regions=risk_regions,
            recommendations=recommendations,
        )
        return jsonify(response.model_dump())

    @app.errorhandler(413)
    def too_large(_err):
        return _json_error(
            code="file_too_large",
            message=f"File exceeds max size of {settings.max_upload_mb} MB.",
            http_status=413,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)

