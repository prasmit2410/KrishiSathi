"""Template-based explanations when LLM is unavailable."""

from __future__ import annotations

from typing import Any


class ExplanationService:
    @staticmethod
    def build_explanations(
        farmer_profile: dict[str, Any],
        validated_crops: list[dict],
        regional: dict[str, Any],
    ) -> dict[str, Any]:
        season = farmer_profile.get("season", "Kharif")
        soil = farmer_profile["soil_type"]
        district = farmer_profile["district"]
        state = farmer_profile["state"]
        land = farmer_profile["land_area"]
        unit = farmer_profile.get("land_unit", "acres")

        recommendations = []
        for item in validated_crops:
            crop = item["crop"]
            note = item.get("note") or ""
            explanation = (
                f"{crop} is recommended for your {soil} soil in {district}, {state} during the {season} season. "
                f"It aligns with regional patterns where crops like {', '.join(regional.get('dominant_crops', [])[:3])} are commonly grown."
            )
            if note:
                explanation += f" Note: {note}"
            recommendations.append({"crop_name": crop, "explanation": explanation})

        top = validated_crops[0]["crop"] if validated_crops else "the recommended crops"
        summary = (
            f"Based on your {land} {unit} farm with {soil} soil in {district}, {state}, "
            f"{top} is the top recommendation for the {season} season."
        )

        return {"summary": summary, "recommendations": recommendations}
