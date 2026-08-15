"""ML crop suitability prediction service."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from backend.app.core.config import Config
from backend.app.core.constants import CROPS

logger = logging.getLogger(__name__)


class MLPredictionService:
    _artifact: dict | None = None

    @classmethod
    def _load_artifact(cls) -> dict:
        if cls._artifact is None:
            model_path = Path(Config.ML_MODEL_PATH)
            if not model_path.exists():
                from ml.crop_recommendation.train import train

                train()
            cls._artifact = joblib.load(model_path)
        return cls._artifact

    @classmethod
    def predict(cls, farmer_profile: dict[str, Any]) -> dict[str, Any]:
        artifact = cls._load_artifact()
        model = artifact["model"]
        encoders = artifact["feature_encoders"]
        crop_encoder = artifact["crop_encoder"]
        feature_cols = artifact["feature_cols"]

        climate_zone = farmer_profile.get("climate_zone", "Semi-arid")
        row = {
            "state": farmer_profile["state"],
            "district": farmer_profile["district"],
            "soil_type": farmer_profile["soil_type"],
            "season": farmer_profile.get("season", "Kharif"),
            "irrigation_available": int(farmer_profile.get("irrigation_available", True)),
            "land_area": farmer_profile["land_area"],
            "climate_zone": climate_zone,
        }

        features = []
        for col in feature_cols:
            le = encoders[col]
            val = str(row[col])
            if val not in le.classes_:
                val = le.classes_[0]
            features.append(le.transform([val])[0])

        X = np.array([features])
        proba = model.predict_proba(X)[0]
        classes = crop_encoder.classes_

        predictions = []
        for idx in proba.argsort()[::-1]:
            crop = classes[idx]
            if crop in CROPS:
                score = float(proba[idx])
                confidence = "high" if score >= 0.4 else "medium" if score >= 0.2 else "low"
                predictions.append({"crop": crop, "score": round(score, 4), "confidence": confidence})

        return {
            "predictions": predictions[:8],
            "model_version": Config.ML_MODEL_VERSION,
            "features_used": feature_cols,
            "top_prediction": predictions[0] if predictions else None,
        }

    @classmethod
    def rule_based_fallback(cls, farmer_profile: dict[str, Any]) -> dict[str, Any]:
        from backend.app.core.constants import SEASON_CROPS, SOIL_CROP_COMPATIBILITY

        soil = farmer_profile["soil_type"]
        season = farmer_profile.get("season", "Kharif")
        compatible = set(SOIL_CROP_COMPATIBILITY.get(soil, CROPS))
        seasonal = set(SEASON_CROPS.get(season, CROPS))
        candidates = list(compatible & seasonal & set(CROPS)) or list(seasonal & set(CROPS)) or CROPS[:5]

        predictions = []
        for i, crop in enumerate(candidates[:5]):
            score = round(0.85 - i * 0.1, 2)
            predictions.append({"crop": crop, "score": score, "confidence": "medium"})

        return {
            "predictions": predictions,
            "model_version": "rule_fallback_v1.0",
            "features_used": ["soil_type", "season"],
            "top_prediction": predictions[0] if predictions else None,
            "method": "rule_based_fallback",
        }
