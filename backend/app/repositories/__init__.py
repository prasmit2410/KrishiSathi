"""
Database repositories for Krishi Sathi application
"""

from uuid import UUID
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import (
    FarmerProfile,
    RecommendationRequest,
    RecommendationResult,
    CropRecommendation,
    AgentExecution,
    ToolExecution,
    RegionalContext,
)


class FarmerProfileRepository:
    """Repository for FarmerProfile operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, **kwargs) -> FarmerProfile:
        """Create new farmer profile"""
        profile = FarmerProfile(**kwargs)
        self.session.add(profile)
        self.session.commit()
        return profile
    
    def get_by_id(self, profile_id: UUID) -> Optional[FarmerProfile]:
        """Get farmer profile by ID"""
        return self.session.query(FarmerProfile).filter(FarmerProfile.id == profile_id).first()


class RecommendationRequestRepository:
    """Repository for RecommendationRequest operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, farmer_profile_id: UUID, **kwargs) -> RecommendationRequest:
        """Create new recommendation request"""
        request = RecommendationRequest(farmer_profile_id=farmer_profile_id, **kwargs)
        self.session.add(request)
        self.session.commit()
        return request
    
    def get_by_id(self, request_id: UUID) -> Optional[RecommendationRequest]:
        """Get recommendation request by ID"""
        return self.session.query(RecommendationRequest).filter(
            RecommendationRequest.id == request_id
        ).first()
    
    def update_status(self, request_id: UUID, status: str, error_message: str = None) -> RecommendationRequest:
        """Update request status"""
        request = self.get_by_id(request_id)
        if request:
            request.status = status
            request.error_message = error_message
            if status == "success":
                request.completed_at = datetime.utcnow()
            self.session.commit()
        return request


class RecommendationResultRepository:
    """Repository for RecommendationResult operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        request_id: UUID,
        summary: str,
        disclaimer: str,
        model_version: str,
        processing_time_ms: int
    ) -> RecommendationResult:
        """Create new recommendation result"""
        result = RecommendationResult(
            request_id=request_id,
            summary=summary,
            disclaimer=disclaimer,
            model_version=model_version,
            processing_time_ms=processing_time_ms
        )
        self.session.add(result)
        self.session.commit()
        return result
    
    def get_by_request_id(self, request_id: UUID) -> Optional[RecommendationResult]:
        """Get result by request ID"""
        return self.session.query(RecommendationResult).filter(
            RecommendationResult.request_id == request_id
        ).first()


class CropRecommendationRepository:
    """Repository for CropRecommendation operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, result_id: UUID, **kwargs) -> CropRecommendation:
        """Create new crop recommendation"""
        crop = CropRecommendation(result_id=result_id, **kwargs)
        self.session.add(crop)
        self.session.commit()
        return crop
    
    def create_batch(self, result_id: UUID, crops_data: List[dict]) -> List[CropRecommendation]:
        """Create multiple crop recommendations"""
        crops = [CropRecommendation(result_id=result_id, **data) for data in crops_data]
        self.session.add_all(crops)
        self.session.commit()
        return crops
    
    def get_by_result_id(self, result_id: UUID) -> List[CropRecommendation]:
        """Get all crops for a recommendation result"""
        return self.session.query(CropRecommendation).filter(
            CropRecommendation.result_id == result_id
        ).order_by(CropRecommendation.rank).all()


class AgentExecutionRepository:
    """Repository for AgentExecution operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        request_id: UUID,
        agent_name: str,
        llm_model: str,
        tools_called: list,
        processing_time_ms: int,
        status: str = "success",
        token_usage: dict = None,
        error_message: str = None
    ) -> AgentExecution:
        """Create new agent execution log"""
        execution = AgentExecution(
            request_id=request_id,
            agent_name=agent_name,
            llm_model=llm_model,
            tools_called=tools_called,
            processing_time_ms=processing_time_ms,
            status=status,
            token_usage=token_usage,
            error_message=error_message
        )
        self.session.add(execution)
        self.session.commit()
        return execution
    
    def get_by_request_id(self, request_id: UUID) -> Optional[AgentExecution]:
        """Get agent execution by request ID"""
        return self.session.query(AgentExecution).filter(
            AgentExecution.request_id == request_id
        ).first()


class ToolExecutionRepository:
    """Repository for ToolExecution operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        agent_execution_id: UUID,
        tool_name: str,
        input_data: dict,
        output_data: dict,
        processing_time_ms: int,
        status: str = "success",
        error_message: str = None
    ) -> ToolExecution:
        """Create new tool execution log"""
        execution = ToolExecution(
            agent_execution_id=agent_execution_id,
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            processing_time_ms=processing_time_ms,
            status=status,
            error_message=error_message
        )
        self.session.add(execution)
        self.session.commit()
        return execution
    
    def get_by_agent_execution_id(self, agent_execution_id: UUID) -> List[ToolExecution]:
        """Get all tool executions for an agent"""
        return self.session.query(ToolExecution).filter(
            ToolExecution.agent_execution_id == agent_execution_id
        ).all()


class RegionalContextRepository:
    """Repository for RegionalContext operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, **kwargs) -> RegionalContext:
        """Create new regional context"""
        context = RegionalContext(**kwargs)
        self.session.add(context)
        self.session.commit()
        return context
    
    def get_by_state_district(self, state: str, district: str) -> Optional[RegionalContext]:
        """Get regional context by state and district"""
        return self.session.query(RegionalContext).filter(
            RegionalContext.state == state,
            RegionalContext.district == district
        ).first()
    
    def get_all_districts_for_state(self, state: str) -> List[RegionalContext]:
        """Get all districts for a state"""
        return self.session.query(RegionalContext).filter(
            RegionalContext.state == state
        ).all()
    
    def update(self, context_id: UUID, **kwargs) -> RegionalContext:
        """Update regional context"""
        context = self.session.query(RegionalContext).filter(
            RegionalContext.id == context_id
        ).first()
        if context:
            for key, value in kwargs.items():
                setattr(context, key, value)
            context.updated_at = datetime.utcnow()
            self.session.commit()
        return context
