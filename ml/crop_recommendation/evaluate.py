"""
Model evaluation and metrics calculation
"""

import json
import logging
from typing import Dict, List, Tuple, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    top_k_accuracy_score
)
from sklearn.ensemble import RandomForestClassifier
import pandas as pd


logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance on test data"""
    
    def __init__(self, model: RandomForestClassifier):
        """
        Initialize evaluator with a trained model.
        
        Args:
            model: Trained scikit-learn model
        """
        self.model = model
        self.evaluation_results = {}
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        top_k_values: List[int] = [1, 3, 5]
    ) -> Dict[str, Any]:
        """
        Evaluate model on test set.
        
        Args:
            X_test: Test features
            y_test: Test labels
            top_k_values: K values for top-k accuracy
        
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            # Get predictions
            y_pred = self.model.predict(X_test)
            y_proba = self.model.predict_proba(X_test)
            
            # Calculate metrics
            results = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "f1_macro": float(f1_score(y_test, y_pred, average='macro', zero_division=0)),
                "f1_weighted": float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
            }
            
            # Top-k accuracy
            for k in top_k_values:
                if k <= len(self.model.classes_):
                    try:
                        top_k_acc = top_k_accuracy_score(y_test, y_proba, k=k)
                        results[f"top_{k}_accuracy"] = float(top_k_acc)
                    except Exception as e:
                        logger.warning(f"Could not calculate top-{k} accuracy: {e}")
            
            # Classification report
            results["classification_report"] = classification_report(
                y_test, y_pred, output_dict=True, zero_division=0
            )
            
            # Confusion matrix
            results["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
            
            # Model info
            results["model_info"] = {
                "n_classes": len(self.model.classes_),
                "n_features": self.model.n_features_in_,
                "feature_importances": self.model.feature_importances_.tolist() if hasattr(self.model, 'feature_importances_') else []
            }
            
            self.evaluation_results = results
            
            logger.info(f"Evaluation completed. Accuracy: {results['accuracy']:.4f}")
            return results
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evaluation summary"""
        if not self.evaluation_results:
            return {}
        
        return {
            "accuracy": self.evaluation_results.get("accuracy"),
            "f1_macro": self.evaluation_results.get("f1_macro"),
            "top_1_accuracy": self.evaluation_results.get("top_1_accuracy"),
            "top_3_accuracy": self.evaluation_results.get("top_3_accuracy"),
            "top_5_accuracy": self.evaluation_results.get("top_5_accuracy"),
        }
    
    def save_report(self, filepath: str) -> None:
        """
        Save evaluation report to JSON file.
        
        Args:
            filepath: Path to save report
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.evaluation_results, f, indent=2)
            logger.info(f"Evaluation report saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
    
    @staticmethod
    def create_model_card(
        model_name: str,
        model_version: str,
        description: str,
        training_data_source: str,
        evaluation_metrics: Dict[str, float],
        features: List[str],
        classes: List[str],
        limitations: List[str],
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """
        Create a model card documenting the model.
        
        Args:
            model_name: Name of the model
            model_version: Version identifier
            description: Model description
            training_data_source: Source of training data
            evaluation_metrics: Dictionary of evaluation metrics
            features: List of feature names
            classes: List of output classes (crops)
            limitations: Known limitations
            recommendations: Usage recommendations
        
        Returns:
            Model card dictionary
        """
        return {
            "model_name": model_name,
            "model_version": model_version,
            "description": description,
            "training_data": {
                "source": training_data_source,
                "features": features,
                "output_classes": classes,
                "n_classes": len(classes)
            },
            "evaluation": evaluation_metrics,
            "limitations": limitations,
            "recommendations": recommendations,
            "intended_use": "Agricultural crop recommendation for Indian farmers",
            "disclaimer": "This model provides estimates. Actual results may vary based on weather, market, and farming practices."
        }
