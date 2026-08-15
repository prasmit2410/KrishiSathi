import os, sys
sys.path.append(os.getcwd())
from backend.app.services.recommendation_service import RecommendationService
from backend.app.schemas.farmer_input import FarmerInputSchema

data = {
    "state": "Karnataka",
    "district": "Bangalore",
    "village": "TestVillage",
    "land_area": 1.0,
    "land_unit": "acres",
    "soil_type": "Loamy",
    "season": "Kharif",
    "irrigation_available": True,
    "previous_crop": "Wheat"
}

try:
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        inp = FarmerInputSchema(**data)
        res = RecommendationService.create_recommendation(inp)
        print("Result keys:", list(res.keys()))
        print("First recommendation:", res.get('recommendations')[0] if res.get('recommendations') else None)
except Exception as e:
    print("Error:", e)
