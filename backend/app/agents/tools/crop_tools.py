"""Agent tool functions for crop recommendation pipeline."""

from __future__ import annotations

import json
import time
from typing import Any

from backend.app.services.ml_prediction_service import MLPredictionService
from backend.app.services.regional_context_service import RegionalContextService
from backend.app.services.rule_engine_service import RuleEngineService


def get_regional_context(state: str, district: str) -> str:
    """Retrieve regional crop patterns and agricultural context for a state and district."""
    start = time.time()
    result = RegionalContextService.get_context(state, district)
    result["_processing_time_ms"] = int((time.time() - start) * 1000)
    return json.dumps(result)


def predict_crop_suitability(farmer_profile_json: str) -> str:
    """Score crop suitability using the trained ML model for a farmer profile JSON string."""
    start = time.time()
    profile = json.loads(farmer_profile_json)
    regional = RegionalContextService.get_context(profile["state"], profile["district"])
    profile["climate_zone"] = regional.get("climate_zone", "Semi-arid")

    try:
        result = MLPredictionService.predict(profile)
        top = result.get("top_prediction")
        if not top or top["score"] < 0.15:
            result = MLPredictionService.rule_based_fallback(profile)
            result["method"] = "rule_based_fallback"
    except Exception:
        result = MLPredictionService.rule_based_fallback(profile)

    result["_processing_time_ms"] = int((time.time() - start) * 1000)
    return json.dumps(result)


def validate_recommendations(predictions_json: str, farmer_profile_json: str) -> str:
    """Validate and re-rank ML predictions using regional and seasonal rules."""
    start = time.time()
    predictions_data = json.loads(predictions_json)
    profile = json.loads(farmer_profile_json)
    predictions = predictions_data.get("predictions", [])
    result = RuleEngineService.validate(predictions, profile)
    result["_processing_time_ms"] = int((time.time() - start) * 1000)
    return json.dumps(result)


def run_tool_pipeline(farmer_profile: dict[str, Any]) -> dict[str, Any]:
    """Execute all tools in sequence (direct orchestration mode)."""
    tools_called = []
    tool_logs = []

    t0 = time.time()
    regional_raw = get_regional_context(farmer_profile["state"], farmer_profile["district"])
    regional = json.loads(regional_raw)
    tools_called.append("get_regional_context")
    tool_logs.append({"tool": "get_regional_context", "output": regional})

    profile = {**farmer_profile, "climate_zone": regional.get("climate_zone")}
    ml_raw = predict_crop_suitability(json.dumps(profile))
    ml_result = json.loads(ml_raw)
    tools_called.append("predict_crop_suitability")
    tool_logs.append({"tool": "predict_crop_suitability", "output": ml_result})

    val_raw = validate_recommendations(ml_raw, json.dumps(profile))
    validated = json.loads(val_raw)
    tools_called.append("validate_recommendations")
    tool_logs.append({"tool": "validate_recommendations", "output": validated})

    return {
        "regional_context": regional,
        "ml_result": ml_result,
        "validated": validated,
        "tools_called": tools_called,
        "tool_logs": tool_logs,
        "processing_time_ms": int((time.time() - t0) * 1000),
    }
