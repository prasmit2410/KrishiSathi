"""
SQLAlchemy models for Krishi Sathi application
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, Boolean, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FarmerProfile(Base):
    """Farmer profile model"""
    __tablename__ = "farmer_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    village = Column(String(100), nullable=True)
    land_area = Column(Float, nullable=False)
    land_unit = Column(String(20), nullable=False)  # acres or hectares
    soil_type = Column(String(50), nullable=False)
    season = Column(String(20), nullable=True)  # Kharif, Rabi, Zaid
    irrigation_available = Column(Boolean, nullable=True)
    previous_crop = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    requests = relationship("RecommendationRequest", back_populates="farmer_profile")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "state": self.state,
            "district": self.district,
            "village": self.village,
            "land_area": self.land_area,
            "land_unit": self.land_unit,
            "soil_type": self.soil_type,
            "season": self.season,
            "irrigation_available": self.irrigation_available,
            "previous_crop": self.previous_crop,
            "created_at": self.created_at.isoformat()
        }


class RecommendationRequest(Base):
    """Recommendation request model"""
    __tablename__ = "recommendation_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    farmer_profile_id = Column(UUID(as_uuid=True), ForeignKey("farmer_profiles.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, success, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    farmer_profile = relationship("FarmerProfile", back_populates="requests")
    result = relationship("RecommendationResult", uselist=False, back_populates="request")
    agent_execution = relationship("AgentExecution", uselist=False, back_populates="request")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "farmer_profile_id": str(self.farmer_profile_id),
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class RecommendationResult(Base):
    """Recommendation result model"""
    __tablename__ = "recommendation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_requests.id"), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    disclaimer = Column(Text, nullable=False)
    model_version = Column(String(50), nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    request = relationship("RecommendationRequest", back_populates="result")
    crops = relationship("CropRecommendation", back_populates="result", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "request_id": str(self.request_id),
            "summary": self.summary,
            "disclaimer": self.disclaimer,
            "model_version": self.model_version,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat(),
            "crops": [crop.to_dict() for crop in self.crops]
        }


class CropRecommendation(Base):
    """Individual crop recommendation model"""
    __tablename__ = "crop_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_results.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    crop_name = Column(String(100), nullable=False)
    suitability = Column(String(20), nullable=False)  # High, Moderate, Low
    suitability_score = Column(Float, nullable=False)
    estimated_risk = Column(String(20), nullable=True)
    estimated_return_potential = Column(String(20), nullable=True)
    explanation = Column(Text, nullable=False)
    method = Column(String(30), nullable=False, default="ml")  # ml or rule_fallback
    
    # Relationships
    result = relationship("RecommendationResult", back_populates="crops")
    
    def to_dict(self):
        return {
            "rank": self.rank,
            "crop_name": self.crop_name,
            "suitability": self.suitability,
            "suitability_score": self.suitability_score,
            "estimated_risk": self.estimated_risk,
            "estimated_return_potential": self.estimated_return_potential,
            "explanation": self.explanation,
            "method": self.method
        }


class AgentExecution(Base):
    """Agent execution log model"""
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_requests.id"), nullable=False, unique=True)
    agent_name = Column(String(100), nullable=False)
    llm_model = Column(String(100), nullable=False)
    tools_called = Column(JSON, nullable=False)  # List of tool names and timestamps
    token_usage = Column(JSON, nullable=True)  # {input_tokens, output_tokens, total_tokens}
    status = Column(String(20), nullable=False)  # success, error, timeout
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    request = relationship("RecommendationRequest", back_populates="agent_execution")
    tool_executions = relationship("ToolExecution", back_populates="agent_execution", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "request_id": str(self.request_id),
            "agent_name": self.agent_name,
            "llm_model": self.llm_model,
            "tools_called": self.tools_called,
            "token_usage": self.token_usage,
            "status": self.status,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat()
        }


class ToolExecution(Base):
    """Tool execution log model"""
    __tablename__ = "tool_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_execution_id = Column(UUID(as_uuid=True), ForeignKey("agent_executions.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False)  # success, error
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    agent_execution = relationship("AgentExecution", back_populates="tool_executions")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "agent_execution_id": str(self.agent_execution_id),
            "tool_name": self.tool_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat()
        }


class RegionalContext(Base):
    """Regional context data model"""
    __tablename__ = "regional_context"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    climate_zone = Column(String(50), nullable=False)
    dominant_crops = Column(JSON, nullable=False)  # List of crop names
    avg_rainfall_mm = Column(Integer, nullable=True)
    major_soil_types = Column(JSON, nullable=True)  # List of soil types
    kharif_crops = Column(JSON, nullable=True)  # List of crops
    rabi_crops = Column(JSON, nullable=True)  # List of crops
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "state": self.state,
            "district": self.district,
            "climate_zone": self.climate_zone,
            "dominant_crops": self.dominant_crops,
            "avg_rainfall_mm": self.avg_rainfall_mm,
            "major_soil_types": self.major_soil_types,
            "kharif_crops": self.kharif_crops,
            "rabi_crops": self.rabi_crops,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
