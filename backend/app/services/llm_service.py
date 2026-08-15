"""OpenRouter LLM service wrapper with primary + fallback model support."""

from __future__ import annotations

import json
import logging
from typing import Any

import requests

from backend.app.core.config import Config

logger = logging.getLogger(__name__)

# Fallback model used when the primary model fails (rate-limited or unavailable)
_FALLBACK_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class LLMService:
    @classmethod
    def is_available(cls) -> bool:
        return bool(Config.OPENROUTER_API_KEY)

    @classmethod
    def _call_model(cls, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Make a single chat completion call to OpenRouter with the given model."""
        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Krishi Sathi",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": Config.OPENROUTER_MAX_TOKENS,
            "temperature": 0.3,
        }
        response = requests.post(
            f"{Config.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=Config.OPENROUTER_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return {
            "content": content,
            "model": model,
            "tokens": usage.get("total_tokens", 0),
        }

    @classmethod
    def chat(cls, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Call OpenRouter with primary model; fall back to secondary model on failure."""
        if not cls.is_available():
            return {"content": None, "model": None, "tokens": 0}

        primary_model = Config.OPENROUTER_MODEL

        # Try primary model first
        try:
            result = cls._call_model(primary_model, system_prompt, user_prompt)
            logger.debug("OpenRouter call succeeded with primary model: %s", primary_model)
            return result
        except Exception as exc:
            logger.warning(
                "OpenRouter primary model '%s' failed: %s. Trying fallback model '%s'.",
                primary_model,
                exc,
                _FALLBACK_MODEL,
            )

        # Try fallback model
        try:
            result = cls._call_model(_FALLBACK_MODEL, system_prompt, user_prompt)
            logger.info("OpenRouter fallback model '%s' succeeded.", _FALLBACK_MODEL)
            return result
        except Exception as exc:
            logger.warning("OpenRouter fallback model '%s' also failed: %s", _FALLBACK_MODEL, exc)
            return {"content": None, "model": primary_model, "tokens": 0, "error": str(exc)}

    @classmethod
    def generate_explanations(cls, farmer_profile: dict, validated_crops: list[dict], regional: dict) -> dict:
        """Generate farmer-friendly crop explanations via LLM."""
        system = (
            "You are Krishi Sathi, an agricultural advisor for Indian farmers. "
            "Use ONLY the provided tool data. Do not invent suitability scores. "
            "Return valid JSON with keys: summary (string), recommendations (array). "
            "Each recommendation item: crop_name, explanation (2-3 farmer-friendly sentences)."
        )
        user = json.dumps(
            {
                "farmer_profile": farmer_profile,
                "regional_context": regional,
                "validated_crops": validated_crops,
            },
            indent=2,
        )

        result = cls.chat(system, user)
        if result.get("content"):
            try:
                text = result["content"]
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                return {"parsed": json.loads(text.strip()), "llm_model": result["model"], "tokens": result["tokens"]}
            except json.JSONDecodeError:
                pass
        return {"parsed": None, "llm_model": result.get("model"), "tokens": result.get("tokens", 0)}
