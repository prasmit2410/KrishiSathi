"""
Unit tests for ML prediction service
"""

import pytest
from app.services.ml_prediction_service import MLPredictionService
from ml.crop_recommendation.features import FeatureEngineer


class TestFeatureEngineer:
    """Test feature engineering"""
    
    def test_validate_input_valid(self):
        """Test valid input validation"""
        is_valid, msg = FeatureEngineer.validate_input("Black", "Maharashtra", "Pune")
        assert is_valid
        assert msg == ""
    
    def test_validate_input_invalid_soil(self):
        """Test invalid soil type"""
        is_valid, msg = FeatureEngineer.validate_input("InvalidSoil", "Maharashtra", "Pune")
        assert not is_valid
        assert "Invalid soil type" in msg
    
    def test_validate_input_missing_state(self):
        """Test missing state"""
        is_valid, msg = FeatureEngineer.validate_input("Black", None, "Pune")
        assert not is_valid
        assert "Invalid state" in msg
    
    def test_create_features_from_input(self):
        """Test feature creation from farmer input"""
        import pandas as pd
        
        df = FeatureEngineer.create_features_from_input(
            soil_type="Black",
            state="Maharashtra",
            district="Pune",
            season="Kharif",
            irrigation_available=True,
            land_area=2.0
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.loc[0, "soil_type"] == "Black"
        assert df.loc[0, "irrigation_available"] == 1


class TestMLPredictionService:
    """Test ML prediction service"""
    
    def test_service_initialization(self):
        """Test service can be initialized"""
        # This test verifies the service can be instantiated
        # Actual model loading may fail if model file not present
        try:
            service = MLPredictionService()
            assert service is not None
        except FileNotFoundError:
            # Expected if model file doesn't exist in test environment
            pytest.skip("ML model file not available in test environment")
    
    def test_predict_with_invalid_soil_type(self):
        """Test prediction with invalid soil type"""
        service = MLPredictionService()
        
        result = service.predict_crops(
            state="Maharashtra",
            district="Pune",
            soil_type="InvalidType"
        )
        
        assert result["status"] == "error" or result["predictions"] == []
