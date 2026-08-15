"""Generate synthetic training data for crop recommendation model."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backend.app.core.constants import (
    CROPS,
    SEASON_CROPS,
    SOIL_CROP_COMPATIBILITY,
    STATES_DISTRICTS,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "crop_training_data.csv"

CLIMATE_ZONES = {
    "Pune": "Semi-arid",
    "Nashik": "Semi-arid",
    "Aurangabad": "Semi-arid",
    "Nagpur": "Sub-humid",
    "Kolhapur": "Humid",
    "Satara": "Humid",
    "Ahmednagar": "Semi-arid",
    "Solapur": "Arid",
    "Belgaum": "Semi-arid",
    "Hubli": "Semi-arid",
    "Mysore": "Humid",
    "Bangalore Rural": "Semi-arid",
    "Gulbarga": "Semi-arid",
    "Ahmedabad": "Arid",
    "Surat": "Humid",
    "Rajkot": "Semi-arid",
    "Vadodara": "Semi-arid",
    "Junagadh": "Arid",
}


def generate_training_data(n_samples: int = 3000) -> pd.DataFrame:
    np.random.seed(42)
    rows = []

    for _ in range(n_samples):
        state = np.random.choice(list(STATES_DISTRICTS.keys()))
        district = np.random.choice(STATES_DISTRICTS[state])
        soil = np.random.choice(list(SOIL_CROP_COMPATIBILITY.keys()))
        season = np.random.choice(list(SEASON_CROPS.keys()))
        irrigation = np.random.choice([True, False], p=[0.7, 0.3])
        land_area = round(np.random.uniform(0.5, 25), 1)

        compatible = set(SOIL_CROP_COMPATIBILITY.get(soil, CROPS))
        seasonal = set(SEASON_CROPS.get(season, CROPS))
        candidates = list(compatible & seasonal & set(CROPS))

        if not candidates:
            candidates = list(set(CROPS) & seasonal) or CROPS

        # Weight crops by compatibility
        weights = []
        for crop in candidates:
            w = 1.0
            if crop in SOIL_CROP_COMPATIBILITY.get(soil, []):
                w += 2.0
            if crop in SEASON_CROPS.get(season, []):
                w += 1.5
            if irrigation and crop in {"Sugarcane", "Cotton", "Rice"}:
                w += 0.5
            if not irrigation and crop in {"Jowar", "Gram", "Groundnut"}:
                w += 1.0
            weights.append(w)

        weights = np.array(weights)
        weights = weights / weights.sum()
        label = np.random.choice(candidates, p=weights)

        rows.append(
            {
                "state": state,
                "district": district,
                "soil_type": soil,
                "season": season,
                "irrigation_available": int(irrigation),
                "land_area": land_area,
                "climate_zone": CLIMATE_ZONES.get(district, "Semi-arid"),
                "label_crop": label,
            }
        )

    return pd.DataFrame(rows)


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_training_data()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} training samples -> {OUTPUT_PATH}")
    print(df["label_crop"].value_counts().head())


if __name__ == "__main__":
    main()
