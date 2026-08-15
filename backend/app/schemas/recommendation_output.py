"""
Pydantic schemas for recommendation output validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CropRecommendationSchema(BaseModel):
    """Single crop recommendation output schema"""
    rank: int = Field(..., description="Rank of recommendation (1-5)")
    crop_name: str = Field(..., description="Name of recommended crop")
    suitability: str = Field(..., description="Suitability level (High/Moderate/Low)")
    suitability_score: float = Field(..., description="Suitability score (0.0-1.0)", ge=0.0, le=1.0)
    estimated_risk: Optional[str] = Field(None, description="Risk level (Low/Medium/High)")
    estimated_return_potential: Optional[str] = Field(None, description="Return potential (Low/Medium/High)")
    explanation: str = Field(..., description="Human-readable explanation for recommendation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "crop_name": "Soybean",
                "suitability": "High",
                "suitability_score": 0.87,
                "estimated_risk": "Low",
                "estimated_return_potential": "High",
                "explanation": "Soybean thrives in black soil with good drainage. Pune district shows strong historical soybean yields during Kharif with adequate irrigation."
            }
        }


class MetadataSchema(BaseModel):
    """Metadata for recommendation response"""
    model_version: str = Field(..., description="ML model version used")
    agent_execution_id: str = Field(..., description="UUID of agent execution")
    tools_called: List[str] = Field(..., description="List of tools called by agent")
    llm_model: str = Field(..., description="LLM model used for explanations")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")
    generated_at: str = Field(..., description="ISO timestamp of generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_version": "crop_rec_v1.0",
                "agent_execution_id": "exec-abc123",
                "tools_called": ["get_regional_context", "predict_crop_suitability", "validate_recommendations"],
                "llm_model": "openrouter/selected-model",
                "processing_time_ms": 1850,
                "generated_at": "2026-08-14T12:00:00Z"
            }
        }


class FarmerInputSchema(BaseModel):
    """Farmer inputs reflected in response"""
    state: str
    district: str
    village: Optional[str] = None
    land_area: float
    land_unit: str  # acres or hectares
    soil_type: str
    season: Optional[str] = None
    irrigation_available: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "Maharashtra",
                "district": "Pune",
                "village": "Hadapsar",
                "land_area": 2.0,
                "land_unit": "acres",
                "soil_type": "Black",
                "season": "Kharif",
                "irrigation_available": True
            }
        }


class RecommendationResponseSchema(BaseModel):
    """Complete recommendation API response schema"""
    request_id: str = Field(..., description="Unique request ID (UUID)")
    status: str = Field(..., description="Response status (success/error)")
    farmer_inputs: FarmerInputSchema
    recommendations: List[CropRecommendationSchema] = Field(..., description="Ranked crop recommendations (3-5 crops)")
    summary: str = Field(..., description="Plain-language summary paragraph")
    metadata: MetadataSchema
    disclaimer: str = Field(..., description="Mandatory legal disclaimer about estimate accuracy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "success",
                "farmer_inputs": {
                    "state": "Maharashtra",
                    "district": "Pune",
                    "village": "Hadapsar",
                    "land_area": 2.0,
                    "land_unit": "acres",
                    "soil_type": "Black",
                    "season": "Kharif",
                    "irrigation_available": True
                },
                "recommendations": [
                    {
                        "rank": 1,
                        "crop_name": "Soybean",
                        "suitability": "High",
                        "suitability_score": 0.87,
                        "estimated_risk": "Low",
                        "estimated_return_potential": "High",
                        "explanation": "Soybean thrives in black soil with good drainage. Pune district shows strong historical soybean yields during Kharif with adequate irrigation."
                    }
                ],
                "summary": "Based on your 2-acre black soil farm in Pune, Maharashtra, soybean is the top recommendation for Kharif season with irrigation.",
                "metadata": {
                    "model_version": "crop_rec_v1.0",
                    "agent_execution_id": "exec-abc123",
                    "tools_called": ["get_regional_context", "predict_crop_suitability", "validate_recommendations"],
                    "llm_model": "openrouter/selected-model",
                    "processing_time_ms": 1850,
                    "generated_at": "2026-08-14T12:00:00Z"
                },
                "disclaimer": "Recommendations are estimates based on historical patterns and model analysis. Actual results may vary with weather, market conditions, and farming practices. Consult your local Krishi Vigyan Kendra for final decisions."
            }
        }


class ErrorResponseSchema(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Associated request ID if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid soil type provided",
                "details": {
                    "field": "soil_type",
                    "value": "InvalidType",
                    "allowed_values": ["Black", "Red", "Alluvial", "Laterite", "Sandy", "Clay", "Loamy"]
                }
            }
        }
