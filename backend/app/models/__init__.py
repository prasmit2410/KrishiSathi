"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime, timezone

from backend.app.core.database import db


def _utcnow():
    return datetime.now(timezone.utc)


class FarmerProfile(db.Model):
    __tablename__ = "farmer_profiles"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100))
    land_area = db.Column(db.Float, nullable=False)
    land_unit = db.Column(db.String(20), nullable=False, default="acres")
    soil_type = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(20))
    irrigation_available = db.Column(db.Boolean, default=True)
    previous_crop = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=_utcnow)


class RecommendationRequest(db.Model):
    __tablename__ = "recommendation_requests"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_profile_id = db.Column(db.String(36), db.ForeignKey("farmer_profiles.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=_utcnow)
    completed_at = db.Column(db.DateTime)

    farmer_profile = db.relationship("FarmerProfile", backref="requests")


class RecommendationResult(db.Model):
    __tablename__ = "recommendation_results"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = db.Column(db.String(36), db.ForeignKey("recommendation_requests.id"), nullable=False)
    summary = db.Column(db.Text)
    disclaimer = db.Column(db.Text)
    model_version = db.Column(db.String(50))
    processing_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=_utcnow)

    request = db.relationship("RecommendationRequest", backref="results")
    crops = db.relationship("CropRecommendation", backref="result", cascade="all, delete-orphan")


class CropRecommendation(db.Model):
    __tablename__ = "crop_recommendations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    result_id = db.Column(db.String(36), db.ForeignKey("recommendation_results.id"), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    suitability = db.Column(db.String(20))
    suitability_score = db.Column(db.Float)
    estimated_risk = db.Column(db.String(20))
    estimated_return_potential = db.Column(db.String(20))
    explanation = db.Column(db.Text)
    method = db.Column(db.String(30), default="ml")
    images = db.Column(db.Text)



class AgentExecution(db.Model):
    __tablename__ = "agent_executions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = db.Column(db.String(36), db.ForeignKey("recommendation_requests.id"))
    agent_name = db.Column(db.String(100), default="CropRecommendationOrchestrator")
    llm_model = db.Column(db.String(100))
    tools_called = db.Column(db.JSON)
    token_usage = db.Column(db.JSON)
    status = db.Column(db.String(20), default="success")
    processing_time_ms = db.Column(db.Integer)
    orchestration_mode = db.Column(db.String(30), default="direct")
    created_at = db.Column(db.DateTime, default=_utcnow)

    tool_executions = db.relationship("ToolExecution", backref="agent_execution", cascade="all, delete-orphan")


class ToolExecution(db.Model):
    __tablename__ = "tool_executions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_execution_id = db.Column(db.String(36), db.ForeignKey("agent_executions.id"), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    status = db.Column(db.String(20), default="success")
    processing_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=_utcnow)


class RegionalContext(db.Model):
    __tablename__ = "regional_context"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    climate_zone = db.Column(db.String(50))
    dominant_crops = db.Column(db.JSON)
    avg_rainfall_mm = db.Column(db.Integer)
    major_soil_types = db.Column(db.JSON)
    kharif_crops = db.Column(db.JSON)
    rabi_crops = db.Column(db.JSON)

    __table_args__ = (db.UniqueConstraint("state", "district", name="uq_state_district"),)
