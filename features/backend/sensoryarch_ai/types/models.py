from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BBox(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


RiskType = Literal["light", "reflection", "pattern", "combined"]


class RiskRegion(BaseModel):
    id: str = Field(min_length=1)
    type: RiskType
    severity: float = Field(ge=0.0, le=1.0)
    bbox: BBox


class Recommendation(BaseModel):
    region_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    actions: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    timing_ms: int = Field(ge=0)
    heatmap_image: str = Field(min_length=1)
    risk_regions: list[RiskRegion] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)

