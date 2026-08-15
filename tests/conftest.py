"""
Pytest configuration and fixtures
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.database import Base
from app.core.config import Settings


@pytest.fixture(scope="session")
def test_db_url():
    """Test database URL"""
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Create test database engine"""
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine) -> Session:
    """Create test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_config():
    """Test configuration"""
    return Settings(
        database_url="sqlite:///:memory:",
        openrouter_api_key="test-key",
        openrouter_model="test-model",
        log_level="DEBUG"
    )


@pytest.fixture
def farmer_profile_data():
    """Sample farmer profile for testing"""
    return {
        "state": "Maharashtra",
        "district": "Pune",
        "village": "Hadapsar",
        "land_area": 2.0,
        "land_unit": "acres",
        "soil_type": "Black",
        "season": "Kharif",
        "irrigation_available": True
    }


@pytest.fixture
def sample_ml_predictions():
    """Sample ML predictions for testing"""
    return [
        {"crop": "Soybean", "score": 0.87, "confidence": "high"},
        {"crop": "Cotton", "score": 0.82, "confidence": "high"},
        {"crop": "Jowar", "score": 0.71, "confidence": "medium"},
        {"crop": "Sugarcane", "score": 0.65, "confidence": "medium"},
        {"crop": "Wheat", "score": 0.42, "confidence": "low"}
    ]
