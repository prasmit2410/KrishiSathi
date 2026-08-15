"""CrewAI orchestrator and direct orchestration fallback."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from backend.app.agents.tools.crop_tools import run_tool_pipeline
from backend.app.core.config import Config
from backend.app.services.explanation_service import ExplanationService
from backend.app.services.llm_service import LLMService
from backend.app.services.rule_engine_service import RuleEngineService

logger = logging.getLogger(__name__)


class AgentOrchestrationService:
    AGENT_NAME = "CropRecommendationOrchestrator"

    @classmethod
    def run(cls, farmer_profile: dict[str, Any]) -> dict[str, Any]:
        start = time.time()

        if Config.USE_CREWAI and LLMService.is_available():
            try:
                result = cls._run_crewai(farmer_profile)
                result["orchestration_mode"] = "crewai"
                result["processing_time_ms"] = int((time.time() - start) * 1000)
                return result
            except Exception as exc:
                logger.warning("CrewAI orchestration failed, falling back to direct: %s", exc)

        result = cls._run_direct(farmer_profile)
        result["orchestration_mode"] = "direct"
        result["processing_time_ms"] = int((time.time() - start) * 1000)
        return result

    @classmethod
    def _run_direct(cls, farmer_profile: dict[str, Any]) -> dict[str, Any]:
        """Direct execution pipeline without CrewAI.

        Returns a dict containing recommendations, summary, and all tool logs.
        """
        pipeline = run_tool_pipeline(farmer_profile)
        # Extract validated crops and ML result
        validated_crops = pipeline["validated"].get("validated_crops", [])
        ml_result = pipeline.get("ml_result", {})
        # Try to get LLM explanations; fall back to template explanations
        llm_expl = LLMService.generate_explanations(
            farmer_profile, validated_crops, pipeline["regional_context"]
        )
        parsed = llm_expl.get("parsed")
        if not parsed:
            # Use static template explanations
            parsed = ExplanationService.build_explanations(
                farmer_profile, validated_crops, pipeline["regional_context"]
            )
        # Build ranked recommendations using the helper
        recommendations = cls._build_recommendations(
            validated_crops, parsed, ml_result
        )
        # Assemble result dict matching what RecommendationService expects
        return {
            "agent_name": cls.AGENT_NAME,
            "recommendations": recommendations,
            "summary": parsed.get("summary", ""),
            "model_version": ml_result.get("model_version", Config.ML_MODEL_VERSION),
            "regional_context": pipeline.get("regional_context"),
            "ml_result": ml_result,
            "validated": pipeline.get("validated"),
            "tools_called": pipeline.get("tools_called", []),
            "tool_logs": pipeline.get("tool_logs", []),
            "llm_model": llm_expl.get("llm_model"),
            "tokens": llm_expl.get("tokens", 0),
        }

    @classmethod
    def _run_crewai(cls, farmer_profile: dict[str, Any]) -> dict[str, Any]:
        from crewai import Agent, Crew, Process, Task
        from crewai.tools import tool

        from backend.app.agents.tools.crop_tools import (
            get_regional_context,
            predict_crop_suitability,
            validate_recommendations,
        )

        @tool("get_regional_context")
        def regional_tool(state: str, district: str) -> str:
            """Get regional crop patterns for a state and district."""
            return get_regional_context(state, district)

        @tool("predict_crop_suitability")
        def ml_tool(farmer_profile_json: str) -> str:
            """Predict crop suitability from farmer profile JSON."""
            return predict_crop_suitability(farmer_profile_json)

        @tool("validate_recommendations")
        def validate_tool(predictions_json: str, farmer_profile_json: str) -> str:
            """Validate ML predictions with agricultural rules."""
            return validate_recommendations(predictions_json, farmer_profile_json)

        import os

        os.environ["OPENAI_API_KEY"] = Config.OPENROUTER_API_KEY
        os.environ["OPENAI_API_BASE"] = Config.OPENROUTER_BASE_URL
        os.environ["OPENAI_MODEL_NAME"] = Config.OPENROUTER_MODEL

        orchestrator = Agent(
            role="Agricultural Recommendation Coordinator",
            goal="Produce accurate ranked crop recommendations using data tools only",
            backstory=(
                "Expert agricultural advisor that uses ML and rule tools to recommend crops "
                "and explains results clearly to Indian farmers."
            ),
            tools=[regional_tool, ml_tool, validate_tool],
            verbose=Config.CREWAI_VERBOSE,
            llm=f"openai/{Config.OPENROUTER_MODEL}",
            max_iter=Config.CREWAI_MAX_ITERATIONS,
        )

        profile_json = json.dumps(farmer_profile)
        task = Task(
            description=f"""
            Recommend top 3-5 crops for this farmer profile:
            {profile_json}

            Steps:
            1. Call get_regional_context with state and district.
            2. Call predict_crop_suitability with the full farmer profile JSON.
            3. Call validate_recommendations with ML output and farmer profile.
            4. Return a JSON summary of validated crops with scores from tools only.
            """,
            expected_output="JSON with validated crop recommendations from tool outputs",
            agent=orchestrator,
        )

        crew = Crew(agents=[orchestrator], tasks=[task], process=Process.sequential, verbose=Config.CREWAI_VERBOSE)
        crew.kickoff()

        # CrewAI runs tools internally; use direct pipeline for structured output reliability
        return cls._run_direct(farmer_profile)

    @staticmethod
    def _build_recommendations(
        validated_crops: list[dict],
        parsed: dict,
        ml_result: dict,
    ) -> list[dict]:
        explanation_map = {
            item["crop_name"]: item["explanation"]
            for item in parsed.get("recommendations", [])
            if "crop_name" in item
        }
        method = ml_result.get("method", "ml")

        recommendations = []
        for rank, item in enumerate(validated_crops[:5], start=1):
            crop = item["crop"]
            score = item["adjusted_score"]
            recommendations.append(
                {
                    "rank": rank,
                    "crop_name": crop,
                    "suitability": RuleEngineService.score_to_suitability(score),
                    "suitability_score": round(score, 4),
                    "estimated_risk": item.get("estimated_risk", "Medium"),
                    "estimated_return_potential": item.get("estimated_return_potential", "Medium"),
                    "explanation": explanation_map.get(
                        crop,
                        f"{crop} is suitable based on soil, season, and regional patterns.",
                    ),
                    "method": method,
                }
            )
        return recommendations
