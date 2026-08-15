"""
Regional Context Tool - Retrieves agricultural context for a region
"""

from typing import Optional
from crewai.tools import tool
from app.services.regional_context_service import RegionalContextService


@tool("get_regional_context")
def get_regional_context_tool(state: str, district: str) -> dict:
    """
    Retrieve regional agricultural context for a state and district.
    
    This tool provides:
    - Climate zone classification
    - Dominant and historical crops
    - Average rainfall
    - Primary soil types
    - Seasonal crop patterns (Kharif, Rabi, Zaid)
    
    Args:
        state: State name (e.g., "Maharashtra")
        district: District name (e.g., "Pune")
    
    Returns:
        Dictionary with regional context information
    """
    try:
        service = RegionalContextService()
        context = service.get_regional_context(state, district)
        
        if not context:
            return {
                "status": "error",
                "message": f"No regional context found for {district}, {state}",
                "state": state,
                "district": district
            }
        
        return {
            "status": "success",
            "state": context.get("state"),
            "district": context.get("district"),
            "climate_zone": context.get("climate_zone"),
            "dominant_crops": context.get("dominant_crops", []),
            "avg_rainfall_mm": context.get("avg_rainfall_mm"),
            "major_soil_types": context.get("major_soil_types", []),
            "kharif_crops": context.get("kharif_crops", []),
            "rabi_crops": context.get("rabi_crops", [])
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving regional context: {str(e)}",
            "state": state,
            "district": district
        }
