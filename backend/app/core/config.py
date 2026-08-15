"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    PROJECT_ROOT = PROJECT_ROOT
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")


    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'krishi_sathi.db'}")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))
    OPENROUTER_TIMEOUT_SECONDS = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "30"))

    CREWAI_VERBOSE = os.getenv("CREWAI_VERBOSE", "false").lower() == "true"
    CREWAI_MAX_ITERATIONS = int(os.getenv("CREWAI_MAX_ITERATIONS", "3"))
    USE_CREWAI = os.getenv("USE_CREWAI", "true").lower() == "true"
    AGENT_TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))

    ML_MODEL_PATH = os.getenv(
        "ML_MODEL_PATH",
        str(PROJECT_ROOT / "ml" / "crop_recommendation" / "models" / "crop_rec_v1.0.pkl"),
    )
    ML_MODEL_VERSION = os.getenv("ML_MODEL_VERSION", "crop_rec_v1.0")
    ML_CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.5"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    DISCLAIMER = (
        "Recommendations are estimates based on historical patterns and model analysis. "
        "Actual results may vary with weather, market conditions, and farming practices. "
        "Consult your local Krishi Vigyan Kendra for final decisions."
    )
