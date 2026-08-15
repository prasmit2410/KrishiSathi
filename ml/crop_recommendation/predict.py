"""
ML Model inference for crop prediction
"""

import os
import json
import pickle
import logging
from typing import Optional, Dict, List, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from .features import FeatureEngineer


logger = logging.getLogger(__name__)


class CropPredictor:
    """Load and use trained crop recommendation model"""
    
    def __init__(self, model_path: str, metadata_path: str = None):
        """
        Initialize the predictor with a trained model.
        
        Args:
            model_path: Path to saved model file (.pkl or .joblib)
            metadata_path: Path to model metadata JSON file
        """
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.crop_classes = []
        self.model_metadata = {}
        
        self._load_model()
    
    def _load_model(self) -> bool:
        """
        Load the trained model from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                return False
            
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Get crop classes from model
            if hasattr(self.model, 'classes_'):
                self.crop_classes = list(self.model.classes_)
            
            # Load metadata if available
            if self.metadata_path and os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
            
            logger.info(f"Model loaded successfully. Classes: {self.crop_classes}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def predict(
        self,
        soil_type: str,
        state: str,
        district: str,
        season: Optional[str] = None,
        irrigation_available: Optional[bool] = None,
        land_area: Optional[float] = None,
        climate_zone: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Predict crop suitability for given farm conditions.
        
        Args:
            soil_type: Soil type
            state: State name
            district: District name
            season: Season (Kharif/Rabi/Zaid)
            irrigation_available: Whether irrigation is available
            land_area: Land area
            climate_zone: Climate zone
            top_k: Return top K predictions
        
        Returns:
            Dictionary with predictions and metadata
        """
        try:
            # Validate input
            is_valid, error_msg = FeatureEngineer.validate_input(soil_type, state, district)
            if not is_valid:
                return {
                    "status": "error",
                    "message": error_msg,
                    "predictions": []
                }
            
            # Create feature dataframe
            features_df = FeatureEngineer.create_features_from_input(
                soil_type=soil_type,
                state=state,
                district=district,
                season=season,
                irrigation_available=irrigation_available,
                land_area=land_area,
                climate_zone=climate_zone
            )
            
            # Transform features
            X, feature_names = self.feature_engineer.transform(features_df)
            
            if self.model is None:
                return {
                    "status": "error",
                    "message": "Model not loaded",
                    "predictions": []
                }
            
            # Get probability predictions
            probabilities = self.model.predict_proba(X)[0]
            
            # Create predictions
            predictions = []
            for crop, prob in zip(self.crop_classes, probabilities):
                predictions.append({
                    "crop": crop,
                    "score": float(prob),
                    "confidence": self._get_confidence_level(prob)
                })
            
            # Sort by score and get top K
            predictions.sort(key=lambda x: x["score"], reverse=True)
            predictions = predictions[:top_k]
            
            return {
                "status": "success",
                "predictions": predictions,
                "model_version": self.model_metadata.get("version", "unknown"),
                "features_used": feature_names,
                "input_params": {
                    "soil_type": soil_type,
                    "state": state,
                    "district": district,
                    "season": season,
                    "irrigation_available": irrigation_available,
                    "land_area": land_area
                }
            }
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                "status": "error",
                "message": f"Prediction failed: {str(e)}",
                "predictions": []
            }
    
    @staticmethod
    def _get_confidence_level(probability: float) -> str:
        """
        Get confidence level based on probability.
        
        Args:
            probability: Prediction probability
        
        Returns:
            Confidence level string
        """
        if probability >= 0.7:
            return "high"
        elif probability >= 0.5:
            return "medium"
        else:
            return "low"
    
    def batch_predict(
        self,
        inputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Make predictions for multiple inputs.
        
        Args:
            inputs: List of input dictionaries
        
        Returns:
            List of prediction results
        """
        results = []
        for inp in inputs:
            result = self.predict(**inp)
            results.append(result)
        return results
