"""Location and soil type reference routes."""

import json
from pathlib import Path

from flask import Blueprint, jsonify, request

from backend.app.core.constants import SOIL_TYPES, STATES_DISTRICTS

locations_bp = Blueprint("locations", __name__)

# Load pre-translated static location data at startup
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_TRANSLATIONS: dict[str, dict] = {}

for _lang in ("hi", "mr"):
    _path = _PROJECT_ROOT / "frontend" / f"states-and-districts-{_lang}.json"
    if _path.is_file():
        with open(_path, "r", encoding="utf-8") as _f:
            raw = json.load(_f)
            # Build lookup: English state name -> {translated_state, districts: [{id, name}]}
            _TRANSLATIONS[_lang] = {
                item["state"]: {
                    "name": item.get("translated_state", item["state"]),
                    "districts": {d["id"]: d["name"] for d in item.get("districts", [])}
                }
                for item in raw.get("states", [])
            }


@locations_bp.route("/soil-types", methods=["GET"])
def soil_types():
    return jsonify({"soil_types": SOIL_TYPES})


@locations_bp.route("/locations/states", methods=["GET"])
def states():
    lang = request.args.get("lang", "en")
    states_list = list(STATES_DISTRICTS.keys())

    if lang in _TRANSLATIONS:
        lang_map = _TRANSLATIONS[lang]
        result = [{"id": s, "name": lang_map.get(s, {}).get("name", s)} for s in states_list]
    else:
        result = [{"id": s, "name": s} for s in states_list]

    return jsonify({"states": result})


@locations_bp.route("/locations/districts", methods=["GET"])
def districts():
    state = request.args.get("state")
    lang = request.args.get("lang", "en")

    if not state or state not in STATES_DISTRICTS:
        return jsonify({"error": "Valid state query parameter required"}), 400

    districts_en = STATES_DISTRICTS[state]

    if lang in _TRANSLATIONS:
        dist_map = _TRANSLATIONS[lang].get(state, {}).get("districts", {})
        result = [{"id": d, "name": dist_map.get(d, d)} for d in districts_en]
    else:
        result = [{"id": d, "name": d} for d in districts_en]

    return jsonify({"state": state, "districts": result})
