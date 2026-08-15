"""
Rule Validation Tool - Validates and filters ML predictions using business rules
"""

from typing import List, Optional
from crewai.tools import tool
from app.services.rule_engine_service import RuleEngineService


@tool("validate_recommendations")
def validate_recommendations_tool(
    ml_predictions: List[dict],
    state: str,
    district: str,
    soil_type: str,
    land_area: float,
    land_unit: str = "acres",
    season: Optional[str] = None,
    irrigation_available: Optional[bool] = None,
    previous_crop: Optional[str] = None
) -> dict:
    """
    Validate and filter ML crop predictions using business rules.
    
    This tool applies regional and agricultural constraints to ML predictions:
    - Soil compatibility checks
    - Season validity validation
    - Irrigation requirement matching
    - Land area feasibility
    - Regional growing patterns
    - Crop rotation recommendations
    
    Args:
        ml_predictions: List of ML predictions with crop names and scores
        state: State name
        district: District name
        soil_type: Farmer's soil type
        land_area: Farmer's land area
        land_unit: Land unit (acres or hectares)
        season: Farming season (optional)
        irrigation_available: Whether irrigation available (optional)
        previous_crop: Previous crop grown (optional)
    
    Returns:
        Dictionary with validated, re-ranked crops and rule notes
    """
    try:
        service = RuleEngineService()
        
        # Prepare farmer profile
        farmer_profile = {
            "state": state,
            "district": district,
            "soil_type": soil_type,
            "land_area": land_area,
            "land_unit": land_unit,
            "season": season,
            "irrigation_available": irrigation_available,
            "previous_crop": previous_crop
        }
        
        # Validate predictions
        validated = service.validate_recommendations(ml_predictions, farmer_profile)
        
        if not validated or validated.get("status") == "error":
            return {
                "status": "error",
                "message": validated.get("message", "Validation failed"),
                "validated_crops": [],
                "fallback": True
            }
        
        return {
            "status": "success",
            "validated_crops": validated.get("validated_crops", []),
            "rules_applied": validated.get("rules_applied", []),
            "warnings": validated.get("warnings", []),
            "fallback": False
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during recommendation validation: {str(e)}",
            "validated_crops": [],
            "fallback": True
        }
