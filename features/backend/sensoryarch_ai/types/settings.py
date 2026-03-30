from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENSORYARCH_", env_file=".env", extra="ignore")

    max_upload_mb: int = Field(default=10, ge=1, le=100)
    max_image_side_px: int = Field(default=1280, ge=256, le=4096)

    light_weight: float = Field(default=0.45, ge=0.0, le=1.0)
    reflection_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    pattern_weight: float = Field(default=0.20, ge=0.0, le=1.0)

    light_v_threshold: int = Field(default=220, ge=0, le=255)
    reflection_s_threshold: int = Field(default=60, ge=0, le=255)

    pattern_edge_density_scale: float = Field(default=1.0, ge=0.1, le=10.0)


def load_settings() -> AppSettings:
    return AppSettings()

