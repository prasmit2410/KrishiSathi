"""Regional agricultural context lookup service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.core.database import db
from backend.app.models import RegionalContext

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SEED_PATH = PROJECT_ROOT / "data" / "seeds" / "regional_context.json"


class RegionalContextService:
    @staticmethod
    def seed_if_empty():
        if RegionalContext.query.count() > 0:
            return
        if not SEED_PATH.exists():
            return
        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        for entry in data:
            db.session.add(
                RegionalContext(
                    state=entry["state"],
                    district=entry["district"],
                    climate_zone=entry.get("climate_zone"),
                    dominant_crops=entry.get("dominant_crops", []),
                    avg_rainfall_mm=entry.get("avg_rainfall_mm"),
                    major_soil_types=entry.get("major_soil_types", []),
                    kharif_crops=entry.get("kharif_crops", []),
                    rabi_crops=entry.get("rabi_crops", []),
                )
            )
        db.session.commit()

    @classmethod
    def get_context(cls, state: str, district: str) -> dict[str, Any]:
        record = RegionalContext.query.filter_by(state=state, district=district).first()
        if record:
            return {
                "state": record.state,
                "district": record.district,
                "climate_zone": record.climate_zone,
                "dominant_crops": record.dominant_crops or [],
                "avg_rainfall_mm": record.avg_rainfall_mm,
                "major_soil_types": record.major_soil_types or [],
                "kharif_crops": record.kharif_crops or [],
                "rabi_crops": record.rabi_crops or [],
            }

        return {
            "state": state,
            "district": district,
            "climate_zone": "Semi-arid",
            "dominant_crops": ["Soybean", "Jowar", "Cotton", "Wheat"],
            "avg_rainfall_mm": 700,
            "major_soil_types": ["Black", "Red", "Loamy"],
            "kharif_crops": ["Soybean", "Cotton", "Jowar", "Rice"],
            "rabi_crops": ["Wheat", "Gram", "Sunflower"],
        }
