"""Krishi Sathi Flask application factory."""

from flask import Flask
from flask_cors import CORS

from backend.app.core.config import Config
from backend.app.core.database import db, init_db
from backend.app.api.routes.health import health_bp
from backend.app.api.routes.locations import locations_bp
from backend.app.api.routes.recommendations import recommendations_bp
from backend.app.controllers.translation_controller import translation_controller


def create_app(config: type[Config] | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder="../../frontend",
        static_url_path="",
        template_folder="../../frontend",
    )
    app.config.from_object(config or Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(locations_bp, url_prefix="/api/v1")
    app.register_blueprint(recommendations_bp, url_prefix="/api/v1")
    app.register_blueprint(translation_controller, url_prefix="/api/v1")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/results")
    def results_page():
        return app.send_static_file("results.html")

    return app
