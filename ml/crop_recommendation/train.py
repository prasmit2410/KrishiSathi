"""Train crop recommendation Random Forest model."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "crop_training_data.csv"
MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "crop_rec_v1.0.pkl"
METADATA_PATH = MODEL_DIR / "crop_rec_v1.0_metadata.json"

FEATURE_COLS = [
    "state",
    "district",
    "soil_type",
    "season",
    "irrigation_available",
    "land_area",
    "climate_zone",
]


def train():
    if not DATA_PATH.exists():
        from ml.crop_recommendation.generate_data import main as gen_main

        gen_main()

    df = pd.read_csv(DATA_PATH)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    encoders = {}
    X = pd.DataFrame()
    for col in FEATURE_COLS:
        le = LabelEncoder()
        X[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    crop_encoder = LabelEncoder()
    y = crop_encoder.fit_transform(df["label_crop"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Top-3 accuracy
    proba = model.predict_proba(X_test)
    top3 = sum(
        1 for i, true in enumerate(y_test) if true in proba[i].argsort()[-3:][::-1]
    ) / len(y_test)

    report = classification_report(y_test, y_pred, target_names=crop_encoder.classes_, output_dict=True)

    artifact = {
        "model": model,
        "feature_encoders": encoders,
        "crop_encoder": crop_encoder,
        "feature_cols": FEATURE_COLS,
    }
    joblib.dump(artifact, MODEL_PATH)

    metadata = {
        "version": "crop_rec_v1.0",
        "features": FEATURE_COLS,
        "classes": list(crop_encoder.classes_),
        "top1_accuracy": round(accuracy, 4),
        "top3_accuracy": round(top3, 4),
        "n_samples": len(df),
        "classification_report": report,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Model saved -> {MODEL_PATH}")
    print(f"Top-1 accuracy: {accuracy:.2%}")
    print(f"Top-3 accuracy: {top3:.2%}")
    return metadata


if __name__ == "__main__":
    train()
