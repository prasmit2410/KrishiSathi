"""Crop recommendation API routes."""

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.app.schemas.farmer_input import FarmerInputSchema
from backend.app.services.recommendation_service import RecommendationService

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/recommendations", methods=["POST"])
def create_recommendation():
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "validation_error", "details": ["Request body required"]}), 400
        farmer_input = FarmerInputSchema(**payload)
        result = RecommendationService.create_recommendation(farmer_input)
        return jsonify(result), 200
    except ValidationError as exc:
        return jsonify({"error": "validation_error", "details": exc.errors()}), 400
    except Exception as exc:
        return jsonify({"error": "processing_error", "message": str(exc)}), 422


@recommendations_bp.route("/recommendations/<request_id>", methods=["GET"])
def get_recommendation(request_id: str):
    lang = request.args.get("lang", "en")
    result = RecommendationService.get_recommendation(request_id, lang)
    if not result:
        return jsonify({"error": "not_found", "message": "Recommendation not found"}), 404
    return jsonify(result), 200

