# backend/app/services/translation_service.py
"""Translation service using Sarvam AI API with OpenRouter fallback.
Provides a translate(text, target_lang) method.
"""

from __future__ import annotations

import logging
import functools
import requests
from typing import Any

from backend.app.services.llm_service import LLMService
from backend.app.core.config import Config

logger = logging.getLogger(__name__)

class TranslationService:
    @staticmethod
    def _system_prompt(target_lang: str) -> str:
        return (
            "You are a translation assistant. Translate the given text exactly into "
            f"{target_lang} preserving meaning, tone, and any technical terms. "
            "Return only the translated text without any extra explanation."
        )

    @classmethod
    @functools.lru_cache(maxsize=256)
    def _translate_cached(cls, text: str, target_lang: str) -> dict[str, Any]:
        """Internal cached translation logic to make calls efficient.
        Uses Sarvam AI if API key is set, otherwise falls back to OpenRouter.
        """
        if not text:
            return {"translated": "", "model": None, "tokens": 0}

        # Check if Sarvam API key is available
        api_key = Config.SARVAM_API_KEY
        if api_key:
            # Map standard short codes to Sarvam locale codes
            lang_mapping = {
                "hi": "hi-IN",
                "hindi": "hi-IN",
                "mr": "mr-IN",
                "marathi": "mr-IN"
            }
            target_code = lang_mapping.get(target_lang.lower(), f"{target_lang.lower()}-IN")
            
            url = "https://api.sarvam.ai/translate"
            headers = {
                "Content-Type": "application/json",
                "api-subscription-key": api_key
            }
            payload = {
                "input": text,
                "source_language_code": "en-IN",
                "target_language_code": target_code,
                "speaker_gender": "Male",
                "model": "mayura:v1"
            }
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()
                translated_text = data.get("translated_text", "").strip()
                if translated_text:
                    return {"translated": translated_text, "model": "sarvam:mayura:v1", "tokens": 0}
            except Exception as e:
                logger.error(f"Sarvam translation API failed: {e}")
                # Fall through to OpenRouter fallback

        # Default fallback translation using configured OpenRouter model
        result = LLMService.chat(cls._system_prompt(target_lang), text)
        if not result.get("content"):
            return {"translated": text, "model": result.get("model"), "tokens": result.get("tokens", 0)}
        return {"translated": result["content"].strip(), "model": result.get("model"), "tokens": result.get("tokens", 0)}

    @classmethod
    def translate(cls, text: str, target_lang: str) -> dict[str, Any]:
        """Public translation method that uses caching.
        Returns a dict with translated text, model used, and token count.
        """
        if not text:
            return {"translated": "", "model": None, "tokens": 0}
        # English does not require translation
        if target_lang.lower() in ("en", "english"):
            return {"translated": text, "model": None, "tokens": 0}
        
        # Use cache for translations
        return cls._translate_cached(text, target_lang)
