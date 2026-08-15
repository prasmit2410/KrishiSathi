"""
ML Prediction Tool - Scores crop suitability using trained ML model
"""

from typing import Optional
from crewai.tools import tool
from app.services.ml_prediction_service import MLPredictionService


@tool("predict_crop_suitability")
def predict_crop_suitability_tool(
    state: str,
    district: str,
    soil_type: str,
    season: Optional[str] = None,
    irrigation_available: Optional[bool] = None,
    land_area: Optional[float] = None
) -> dict:
    """
    Predict crop suitability scores using trained ML model.
    
    This tool uses a machine learning model trained on historical crop data
    to score the suitability of various crops for the given farm conditions.
    
    Args:
        state: State name (e.g., "Maharashtra")
        district: District name (e.g., "Pune")
        soil_type: Soil type (e.g., "Black", "Red", "Alluvial")
        season: Farming season (optional: "Kharif", "Rabi", "Zaid")
        irrigation_available: Whether irrigation is available (optional: true/false)
        land_area: Land area in acres/hectares (optional)
    
    Returns:
        Dictionary with ranked crop predictions and scores
    """
    try:
        service = MLPredictionService()
        predictions = service.predict_crops(
            state=state,
            district=district,
            soil_type=soil_type,
            season=season,
            irrigation_available=irrigation_available,
            land_area=land_area
        )
        
        if not predictions or predictions.get("status") == "error":
            return {
                "status": "error",
                "message": predictions.get("message", "ML prediction failed"),
                "fallback": True
            }
        
        return {
            "status": "success",
            "predictions": predictions.get("predictions", []),
            "model_version": predictions.get("model_version"),
            "features_used": predictions.get("features_used", []),
            "confidence_threshold": 0.5,
            "fallback": False
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during crop prediction: {str(e)}",
            "fallback": True
        }
