"""SQLAlchemy database setup."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Check and auto-add 'images' column if not exists
        try:
            engine = db.engine
            inspector = db.inspect(engine)
            columns = [c['name'] for c in inspector.get_columns('crop_recommendations')]
            if 'images' not in columns:
                with engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE crop_recommendations ADD COLUMN images TEXT;"))
                    conn.commit()
        except Exception as e:
            app.logger.warning(f"Auto-migration check failed (possibly first run or different DB): {e}")

        from backend.app.services.regional_context_service import RegionalContextService
        RegionalContextService.seed_if_empty()

