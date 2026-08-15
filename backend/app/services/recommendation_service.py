"""Top-level recommendation service with persistence."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from backend.app.core.config import Config
from backend.app.core.database import db
from backend.app.models import (
    AgentExecution,
    CropRecommendation,
    FarmerProfile,
    RecommendationRequest,
    RecommendationResult,
    ToolExecution,
)
from backend.app.schemas.farmer_input import FarmerInputSchema
from backend.app.services.agent_service import AgentOrchestrationService
from backend.app.services.llm_service import LLMService
from backend.app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for creating and retrieving crop recommendations."""

    @classmethod
    def create_recommendation(cls, input_data: FarmerInputSchema) -> dict[str, Any]:
        """Create a new recommendation from farmer input data."""
        profile_dict = input_data.model_dump()
        language = profile_dict.pop("language", "en") or "en"

        farmer = FarmerProfile(**profile_dict)
        db.session.add(farmer)
        db.session.flush()

        request = RecommendationRequest(farmer_profile_id=farmer.id, status="processing")
        db.session.add(request)
        db.session.flush()

        from backend.app.services.tavily_service import TavilyService  # noqa: PLC0415

        agent_result = AgentOrchestrationService.run(profile_dict)

        # Enrich recommendations with image URLs (top 5)
        for rec in agent_result.get("recommendations", []):
            try:
                images = TavilyService.search_images(rec.get("crop_name", ""), top_n=5)
                rec["images"] = images
            except Exception:  # noqa: BLE001
                logger.error("Tavily image search failed for %s", rec.get("crop_name"))
                rec["images"] = []

        agent_exec = AgentExecution(
            request_id=request.id,
            agent_name=agent_result["agent_name"],
            llm_model=agent_result.get("llm_model"),
            tools_called=agent_result["tools_called"],
            token_usage={"tokens": agent_result.get("tokens", 0)},
            status="success",
            processing_time_ms=agent_result["processing_time_ms"],
            orchestration_mode=agent_result.get("orchestration_mode", "direct"),
        )
        db.session.add(agent_exec)
        db.session.flush()

        for log in agent_result.get("tool_logs", []):
            db.session.add(
                ToolExecution(
                    agent_execution_id=agent_exec.id,
                    tool_name=log["tool"],
                    output_data=log["output"],
                    status="success",
                )
            )

        result = RecommendationResult(
            request_id=request.id,
            summary=agent_result["summary"],
            disclaimer=Config.DISCLAIMER,
            model_version=agent_result.get("model_version", Config.ML_MODEL_VERSION),
            processing_time_ms=agent_result["processing_time_ms"],
        )
        db.session.add(result)
        db.session.flush()

        for rec in agent_result["recommendations"]:
            db.session.add(
                CropRecommendation(
                    result_id=result.id,
                    rank=rec["rank"],
                    crop_name=rec["crop_name"],
                    suitability=rec["suitability"],
                    suitability_score=rec["suitability_score"],
                    estimated_risk=rec["estimated_risk"],
                    estimated_return_potential=rec["estimated_return_potential"],
                    explanation=rec["explanation"],
                    method=rec.get("method", "ml"),
                    images=json.dumps(rec.get("images", [])),
                )
            )

        request.status = "success"
        request.completed_at = datetime.now(timezone.utc)
        db.session.commit()

        response = cls._format_response(request.id, profile_dict, agent_result, agent_exec.id)
        return cls._translate_response(response, language)

    @classmethod
    def get_recommendation(cls, request_id: str, lang: str = "en") -> dict[str, Any] | None:
        """Retrieve an existing recommendation by request ID."""
        request = RecommendationRequest.query.get(request_id)
        if not request or not request.results:
            return None

        result = request.results[0]
        farmer = request.farmer_profile
        profile_dict = {
            "state": farmer.state,
            "district": farmer.district,
            "village": farmer.village,
            "land_area": farmer.land_area,
            "land_unit": farmer.land_unit,
            "soil_type": farmer.soil_type,
            "season": farmer.season,
            "irrigation_available": farmer.irrigation_available,
            "previous_crop": farmer.previous_crop,
        }

        agent_exec = AgentExecution.query.filter_by(request_id=request_id).first()
        agent_result = {
            "recommendations": [
                {
                    "rank": c.rank,
                    "crop_name": c.crop_name,
                    "suitability": c.suitability,
                    "suitability_score": c.suitability_score,
                    "estimated_risk": c.estimated_risk,
                    "estimated_return_potential": c.estimated_return_potential,
                    "explanation": c.explanation,
                    "method": c.method,
                    "images": json.loads(c.images) if c.images else [],
                }
                for c in sorted(result.crops, key=lambda x: x.rank)
            ],
            "summary": result.summary,
            "model_version": result.model_version,
            "processing_time_ms": result.processing_time_ms,
            "tools_called": agent_exec.tools_called if agent_exec else [],
            "llm_model": agent_exec.llm_model if agent_exec else None,
            "orchestration_mode": agent_exec.orchestration_mode if agent_exec else "direct",
        }

        response = cls._format_response(
            request.id,
            profile_dict,
            agent_result,
            agent_exec.id if agent_exec else None,
        )
        return cls._translate_response(response, lang)

    @staticmethod
    def _collect_texts(response: dict) -> list[tuple[str, int | None, str]]:
        """Collect all (field, index, text) tuples needing translation from the response."""
        texts: list[tuple[str, int | None, str]] = []
        if response.get("summary"):
            texts.append(("summary", None, response["summary"]))
        if response.get("disclaimer"):
            texts.append(("disclaimer", None, response["disclaimer"]))
        
        inputs = response.get("farmer_inputs", {})
        for field in ["state", "district", "village", "soil_type", "season", "land_unit"]:
            if inputs.get(field):
                texts.append((field, -1, inputs[field]))

        for i, rec in enumerate(response.get("recommendations", [])):
            for field in [
                "crop_name",
                "suitability",
                "estimated_risk",
                "estimated_return_potential",
                "explanation",
            ]:
                if rec.get(field):
                    texts.append((field, i, rec[field]))
        return texts

    @staticmethod
    def _apply_translations(
        response: dict,
        texts_to_translate: list[tuple[str, int | None, str]],
        translated: list[str],
    ) -> dict:
        """Apply translated strings back onto the response dict."""
        for (field, idx, _), trans in zip(texts_to_translate, translated):
            if idx is None:
                response[field] = trans
            elif idx == -1:
                response["farmer_inputs"][field] = trans
            else:
                response["recommendations"][idx][field] = trans
        return response

    @classmethod
    def _translate_via_sarvam(
        cls,
        response: dict,
        texts_to_translate: list[tuple[str, int | None, str]],
        lang: str,
    ) -> dict:
        """Translate each text field individually via Sarvam AI."""
        translated = [
            TranslationService.translate(orig, lang)["translated"]
            for _, _, orig in texts_to_translate
        ]
        return cls._apply_translations(response, texts_to_translate, translated)

    @classmethod
    def _translate_via_openrouter(
        cls,
        response: dict,
        texts_to_translate: list[tuple[str, int | None, str]],
        lang: str,
    ) -> dict:
        """Bulk-translate all text fields via OpenRouter in a single LLM call."""
        delimited_text = "\n---\n".join(t[2] for t in texts_to_translate)
        system_prompt = (
            "You are a translation assistant. Translate each block of text separated by "
            "'\\n---\\n' "
            f"exactly into {lang}, preserving meaning, tone, and formatting. "
            "Do not add any extra explanations or comments. Return ONLY the translated blocks "
            "separated by '\\n---\\n' exactly as the source separators."
        )

        result = LLMService.chat(system_prompt, delimited_text)
        translated_content = result.get("content", "")
        if not translated_content:
            return response

        translated_blocks = [b.strip() for b in translated_content.split("\n---\n")]
        if len(translated_blocks) == len(texts_to_translate):
            return cls._apply_translations(response, texts_to_translate, translated_blocks)

        # Mismatch — fall back to sequential translation
        logger.warning(
            "Translation block count mismatch: expected %d, got %d. Falling back to sequential.",
            len(texts_to_translate),
            len(translated_blocks),
        )
        return cls._translate_via_sarvam(response, texts_to_translate, lang)

    @classmethod
    def _translate_response(cls, response: dict[str, Any], lang: str) -> dict[str, Any]:
        """Translate the response fields into the requested language."""
        if not lang or lang.lower() == "en":
            return response

        texts_to_translate = cls._collect_texts(response)
        if not texts_to_translate:
            return response

        if Config.SARVAM_API_KEY:
            return cls._translate_via_sarvam(response, texts_to_translate, lang)

        return cls._translate_via_openrouter(response, texts_to_translate, lang)

    @staticmethod
    def _format_response(
        request_id: str,
        profile_dict: dict,
        agent_result: dict,
        agent_exec_id: str | None,
    ) -> dict[str, Any]:
        """Format the final response dict from an agent result."""
        return {
            "request_id": request_id,
            "status": "success",
            "farmer_inputs": profile_dict,
            "recommendations": agent_result["recommendations"],
            "summary": agent_result["summary"],
            "metadata": {
                "model_version": agent_result.get("model_version", Config.ML_MODEL_VERSION),
                "agent_execution_id": agent_exec_id,
                "tools_called": agent_result.get("tools_called", []),
                "llm_model": agent_result.get("llm_model"),
                "processing_time_ms": agent_result.get("processing_time_ms", 0),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "orchestration_mode": agent_result.get("orchestration_mode", "direct"),
            },
            "disclaimer": Config.DISCLAIMER,
        }
