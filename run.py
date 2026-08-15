"""Krishi Sathi local development server."""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up logging to both console and a file for persistent debugging information
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

from backend.app import create_app
from backend.app.core.config import Config




def ensure_model():
    model_path = Path(Config.ML_MODEL_PATH)
    if not model_path.exists():
        print("Training ML model (first run)...")
        from ml.crop_recommendation.train import train

        train()


def main():
    try:
        ensure_model()
        app = create_app()
        # Integrate Flask's logger with our custom logger so request logs are also saved
        flask_logger = logging.getLogger('werkzeug')
        flask_logger.handlers = logger.handlers
        flask_logger.setLevel(logging.INFO)
        logger.info(f"Krishi Sathi Phase 1 running at http://{Config.API_HOST}:{Config.API_PORT}")
        app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)
    except Exception as e:
        logger.exception("Fatal error while running the server")
        raise


if __name__ == "__main__":
    main()
