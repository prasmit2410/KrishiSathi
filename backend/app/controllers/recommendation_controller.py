'''Recommendation controller for Flask API.'''

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.app.schemas.farmer_input import FarmerInputSchema
from backend.app.services.recommendation_service import RecommendationService

# Blueprint for recommendation endpoints
recommendation_controller = Blueprint('recommendation_controller', __name__)

@recommendation_controller.route('/api/v1/recommendations', methods=['POST'])
def create_recommendation():
    """Create a new crop recommendation request.
    Expects JSON payload matching FarmerInputSchema.
    Returns the recommendation result JSON on success.
    """
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

@recommendation_controller.route('/api/v1/recommendations/<request_id>', methods=['GET'])
def get_recommendation(request_id: str):
    """Retrieve an existing recommendation by its request ID."""
    result = RecommendationService.get_recommendation(request_id)
    if not result:
        return jsonify({"error": "not_found", "message": "Recommendation not found"}), 404
    return jsonify(result), 200
