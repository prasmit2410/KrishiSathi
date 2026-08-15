"""Health check routes."""

from flask import Blueprint, jsonify

from backend.app.core.config import Config

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "Krishi Sathi",
            "phase": "1",
            "model_version": Config.ML_MODEL_VERSION,
        }
    )
