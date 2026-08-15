"""Rule-based validation over ML crop predictions."""

from __future__ import annotations

from typing import Any

from backend.app.core.constants import (
    CROP_RETURN,
    CROP_RISK,
    IRRIGATION_REQUIRED,
    MIN_LAND_ACRES,
    SEASON_CROPS,
    SOIL_CROP_COMPATIBILITY,
)


class RuleEngineService:
    @staticmethod
    def _to_acres(land_area: float, land_unit: str) -> float:
        if land_unit == "hectares":
            return land_area * 2.471
        return land_area

    @classmethod
    def validate(cls, predictions: list[dict], farmer_profile: dict[str, Any]) -> dict[str, Any]:
        soil = farmer_profile["soil_type"]
        season = farmer_profile.get("season", "Kharif")
        irrigation = farmer_profile.get("irrigation_available", True)
        land_acres = cls._to_acres(farmer_profile["land_area"], farmer_profile.get("land_unit", "acres"))
        previous_crop = farmer_profile.get("previous_crop")

        soil_compatible = set(SOIL_CROP_COMPATIBILITY.get(soil, []))
        season_valid = set(SEASON_CROPS.get(season, []))

        validated = []
        for pred in predictions:
            crop = pred["crop"]
            original_score = pred["score"]
            adjusted_score = original_score
            rules_passed = []
            rules_failed = []
            status = "approved"
            note = None

            if crop in soil_compatible:
                rules_passed.append("soil_compatible")
            else:
                rules_failed.append("soil_incompatible")
                adjusted_score *= 0.5
                status = "downgraded"
                note = f"{crop} is not typically grown in {soil} soil"

            if crop in season_valid:
                rules_passed.append("season_valid")
            else:
                rules_failed.append("season_invalid")
                adjusted_score *= 0.3
                status = "removed" if adjusted_score < 0.15 else "downgraded"
                note = note or f"{crop} is not a typical {season} season crop"

            if crop in IRRIGATION_REQUIRED:
                if irrigation:
                    rules_passed.append("irrigation_adequate")
                else:
                    rules_failed.append("irrigation_required")
                    adjusted_score *= 0.4
                    status = "downgraded"
                    note = note or f"{crop} typically requires irrigation"

            min_acres = MIN_LAND_ACRES.get(crop)
            if min_acres and land_acres < min_acres:
                rules_failed.append("insufficient_land_area")
                adjusted_score *= 0.6
                status = "downgraded"
                note = note or f"{crop} typically needs at least {min_acres} acres for viability"

            if previous_crop and previous_crop.lower() == crop.lower():
                rules_failed.append("same_as_previous_crop")
                note = note or "Consider crop rotation for soil health"

            if status == "removed":
                continue

            validated.append(
                {
                    "crop": crop,
                    "original_score": round(original_score, 4),
                    "adjusted_score": round(adjusted_score, 4),
                    "rules_passed": rules_passed,
                    "rules_failed": rules_failed,
                    "status": status,
                    "note": note,
                    "estimated_risk": CROP_RISK.get(crop, "Medium"),
                    "estimated_return_potential": CROP_RETURN.get(crop, "Medium"),
                }
            )

        validated.sort(key=lambda x: x["adjusted_score"], reverse=True)
        return {"validated_crops": validated[:5]}

    @staticmethod
    def score_to_suitability(score: float) -> str:
        if score >= 0.6:
            return "High"
        if score >= 0.35:
            return "Moderate"
        return "Low"
