"""WSGI entrypoint for production deployment (Render, Gunicorn, etc.)"""
import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Minimal logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# Ensure ML model is available before starting
from backend.app.core.config import Config

model_path = Path(Config.ML_MODEL_PATH)
if not model_path.exists():
    from ml.crop_recommendation.train import train
    train()

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
