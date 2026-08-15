"""Shared constants for Krishi Sathi Phase 1."""

SOIL_TYPES = [
    "Black",
    "Red",
    "Alluvial",
    "Laterite",
    "Sandy",
    "Clay",
    "Loamy",
]

SEASONS = ["Kharif", "Rabi", "Zaid"]

LAND_UNITS = ["acres", "hectares"]

CROPS = [
    "Soybean",
    "Cotton",
    "Jowar",
    "Wheat",
    "Rice",
    "Sugarcane",
    "Gram",
    "Sunflower",
    "Maize",
    "Groundnut",
    "Tur",
    "Onion",
]

# Load state-district mapping from JSON file
import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = _PROJECT_ROOT / "frontend" / "states-and-districts.json"
if DATA_PATH.is_file():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
        # Expected format: {"states": [{"state": "Name", "districts": [...]}, ...]}
        if isinstance(raw, dict) and "states" in raw:
            STATES_DISTRICTS = {item["state"]: item.get("districts", []) for item in raw["states"]}
        else:
            # Fallback if the file already matches the expected mapping
            STATES_DISTRICTS = raw if isinstance(raw, dict) else {}
else:
    # Fallback empty mapping (should be populated in data file)
    STATES_DISTRICTS = {}




# Soil → compatible crops (base suitability)
SOIL_CROP_COMPATIBILITY: dict[str, list[str]] = {
    "Black": ["Soybean", "Cotton", "Jowar", "Wheat", "Gram", "Sunflower"],
    "Red": ["Groundnut", "Jowar", "Tur", "Sunflower", "Cotton", "Maize"],
    "Alluvial": ["Rice", "Wheat", "Sugarcane", "Maize", "Gram", "Onion"],
    "Laterite": ["Cashew", "Coconut", "Rubber", "Groundnut", "Tur"],
    "Sandy": ["Groundnut", "Bajra", "Watermelon", "Moong"],
    "Clay": ["Rice", "Wheat", "Sugarcane", "Gram"],
    "Loamy": ["Soybean", "Wheat", "Cotton", "Maize", "Gram", "Sunflower"],
}

# Season → typical crops
SEASON_CROPS: dict[str, list[str]] = {
    "Kharif": ["Soybean", "Cotton", "Jowar", "Rice", "Maize", "Groundnut", "Tur", "Sunflower"],
    "Rabi": ["Wheat", "Gram", "Sunflower", "Onion"],
    "Zaid": ["Sunflower", "Onion", "Maize", "Groundnut"],
}

# Crops requiring irrigation
IRRIGATION_REQUIRED = {"Sugarcane", "Rice", "Cotton", "Onion"}

# Minimum land area (acres) for viability
MIN_LAND_ACRES: dict[str, float] = {
    "Sugarcane": 5.0,
    "Cotton": 1.0,
    "Rice": 0.5,
}

# Risk and return heuristics per crop
CROP_RISK: dict[str, str] = {
    "Soybean": "Low",
    "Cotton": "Medium",
    "Jowar": "Low",
    "Wheat": "Low",
    "Rice": "Medium",
    "Sugarcane": "Medium",
    "Gram": "Low",
    "Sunflower": "Low",
    "Maize": "Low",
    "Groundnut": "Low",
    "Tur": "Low",
    "Onion": "Medium",
}

CROP_RETURN: dict[str, str] = {
    "Soybean": "High",
    "Cotton": "High",
    "Jowar": "Medium",
    "Wheat": "Medium",
    "Rice": "Medium",
    "Sugarcane": "High",
    "Gram": "Medium",
    "Sunflower": "Medium",
    "Maize": "Medium",
    "Groundnut": "Medium",
    "Tur": "Medium",
    "Onion": "High",
}
