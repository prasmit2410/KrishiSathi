"""
Feature engineering for ML crop recommendation model
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.preprocessing import LabelEncoder
import pickle


class FeatureEngineer:
    """Feature engineering for crop recommendation"""
    
    # Supported values
    SOIL_TYPES = ["Black", "Red", "Alluvial", "Laterite", "Sandy", "Clay", "Loamy"]
    SEASONS = ["Kharif", "Rabi", "Zaid"]
    CLIMATE_ZONES = ["Tropical", "Sub-tropical", "Temperate", "Semi-arid", "Arid"]
    
    def __init__(self):
        self.encoders = {}
        self.feature_names = []
    
    def fit(self, df: pd.DataFrame) -> 'FeatureEngineer':
        """
        Fit feature encoders on training data.
        
        Args:
            df: Training dataframe with original features
            
        Returns:
            Self for chaining
        """
        # Create label encoders for categorical features
        categorical_features = ['soil_type', 'state', 'district', 'season', 'climate_zone']
        
        for feature in categorical_features:
            if feature in df.columns:
                self.encoders[feature] = LabelEncoder()
                self.encoders[feature].fit(df[feature].astype(str))
        
        return self
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, list]:
        """
        Transform raw features to model input format.
        
        Args:
            df: Dataframe with raw features
            
        Returns:
            Tuple of (transformed features array, feature names list)
        """
        df_copy = df.copy()
        features = []
        feature_names = []
        
        # Encode categorical features
        for col in ['soil_type', 'state', 'district', 'season', 'climate_zone']:
            if col in df_copy.columns:
                if col in self.encoders:
                    try:
                        df_copy[f'{col}_encoded'] = self.encoders[col].transform(
                            df_copy[col].astype(str)
                        )
                        features.append(df_copy[f'{col}_encoded'].values)
                        feature_names.append(f'{col}_encoded')
                    except ValueError:
                        # Handle unknown categories
                        df_copy[f'{col}_encoded'] = 0
                        features.append(df_copy[f'{col}_encoded'].values)
                        feature_names.append(f'{col}_encoded')
        
        # Numeric features
        numeric_features = ['irrigation_available', 'land_area_normalized']
        for col in numeric_features:
            if col in df_copy.columns:
                features.append(df_copy[col].values)
                feature_names.append(col)
        
        # Regional frequency feature
        if 'regional_crop_frequency' in df_copy.columns:
            features.append(df_copy['regional_crop_frequency'].values)
            feature_names.append('regional_crop_frequency')
        
        # Combine all features
        X = np.column_stack(features) if features else np.array([])
        
        self.feature_names = feature_names
        
        return X, feature_names
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, list]:
        """
        Fit and transform in one step.
        
        Args:
            df: Training dataframe
            
        Returns:
            Tuple of (transformed features, feature names)
        """
        self.fit(df)
        return self.transform(df)
    
    def save(self, filepath: str) -> None:
        """Save encoders to file"""
        pickle.dump(self.encoders, open(filepath, 'wb'))
    
    def load(self, filepath: str) -> None:
        """Load encoders from file"""
        self.encoders = pickle.load(open(filepath, 'rb'))
    
    def get_feature_names(self) -> list:
        """Get list of feature names"""
        return self.feature_names
    
    @staticmethod
    def create_features_from_input(
        soil_type: str,
        state: str,
        district: str,
        season: str = None,
        irrigation_available: bool = None,
        land_area: float = None,
        climate_zone: str = None,
        regional_crop_frequency: float = None
    ) -> pd.DataFrame:
        """
        Create feature dataframe from farmer input.
        
        Args:
            soil_type: Soil type
            state: State
            district: District
            season: Season (optional)
            irrigation_available: Irrigation availability (optional)
            land_area: Land area (optional)
            climate_zone: Climate zone (optional)
            regional_crop_frequency: Crop frequency in region (optional)
        
        Returns:
            Feature dataframe
        """
        data = {
            'soil_type': [soil_type],
            'state': [state],
            'district': [district],
            'season': [season or 'Kharif'],
            'irrigation_available': [1 if irrigation_available else 0],
            'land_area_normalized': [np.log1p(land_area) if land_area else 0],
            'climate_zone': [climate_zone or 'Semi-arid'],
            'regional_crop_frequency': [regional_crop_frequency or 0.5]
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def validate_input(
        soil_type: str,
        state: str,
        district: str
    ) -> Tuple[bool, str]:
        """
        Validate input features.
        
        Args:
            soil_type: Soil type to validate
            state: State to validate
            district: District to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if soil_type not in FeatureEngineer.SOIL_TYPES:
            return False, f"Invalid soil type: {soil_type}"
        
        if not state or not isinstance(state, str):
            return False, "Invalid state"
        
        if not district or not isinstance(district, str):
            return False, "Invalid district"
        
        return True, ""
