"""Pydantic schemas for API validation."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.core.constants import LAND_UNITS, SEASONS, SOIL_TYPES, STATES_DISTRICTS


class FarmerInputSchema(BaseModel):
    state: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)
    village: Optional[str] = Field(None, max_length=100)
    land_area: float = Field(..., gt=0, le=500)
    land_unit: Literal["acres", "hectares"] = "acres"
    soil_type: str
    season: Optional[str] = "Kharif"
    irrigation_available: Optional[bool] = True
    previous_crop: Optional[str] = None
    language: Optional[str] = "en"


    @field_validator("soil_type")
    @classmethod
    def validate_soil(cls, v: str) -> str:
        if v not in SOIL_TYPES:
            raise ValueError(f"soil_type must be one of: {', '.join(SOIL_TYPES)}")
        return v

    @field_validator("season")
    @classmethod
    def validate_season(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in SEASONS:
            raise ValueError(f"season must be one of: {', '.join(SEASONS)}")
        return v

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: str, info) -> str:
        state = info.data.get("state")
        if state and state in STATES_DISTRICTS:
            if v not in STATES_DISTRICTS[state]:
                raise ValueError(f"district '{v}' is not valid for state '{state}'")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        if v not in STATES_DISTRICTS:
            raise ValueError(f"state must be one of: {', '.join(STATES_DISTRICTS.keys())}")
        return v


class CropRecommendationItem(BaseModel):
    rank: int
    crop_name: str
    suitability: str
    suitability_score: float
    estimated_risk: str
    estimated_return_potential: str
    explanation: str
    method: str = "ml"


class RecommendationMetadata(BaseModel):
    model_version: str
    agent_execution_id: Optional[str] = None
    tools_called: list[str]
    llm_model: Optional[str] = None
    processing_time_ms: int
    generated_at: str
    orchestration_mode: str = "direct"


class RecommendationResponse(BaseModel):
    request_id: str
    status: str
    farmer_inputs: dict
    recommendations: list[CropRecommendationItem]
    summary: str
    metadata: RecommendationMetadata
    disclaimer: str
