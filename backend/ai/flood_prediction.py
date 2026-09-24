"""
AI Flood Prediction Module using Scikit-Learn
This module provides:
- Data preprocessing and feature engineering
- Model training (Random Forest, Decision Tree)
- Flood risk prediction
- Model evaluation and persistence
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FloodPredictionModel:
    """
    AI Flood Prediction Model using Machine Learning.
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the flood prediction model.
        
        Args:
            model_type: Type of model ('random_forest' or 'decision_tree')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = [
            'water_level_cm',
            'hour_of_day',
            'day_of_week',
            'month',
            'rate_of_change',
            'avg_last_1h',
            'avg_last_6h',
            'avg_last_24h',
            'max_last_24h',
            'min_last_24h'
        ]
        self.is_trained = False
        self.model_metadata = {}
        
    def generate_sample_data(self, num_samples: int = 1000) -> pd.DataFrame:
        """
        Generate realistic sample training data for demonstration.
        In production, this would be replaced with actual historical data.
        
        Args:
            num_samples: Number of samples to generate
            
        Returns:
            DataFrame with synthetic water level data
        """
        logger.info(f"Generating {num_samples} sample data points...")
        
        np.random.seed(42)
        
        # Generate timestamps
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        timestamps = pd.date_range(start=start_date, end=end_date, periods=num_samples)
        
        data = []
        
        for i, timestamp in enumerate(timestamps):
            # Simulate seasonal patterns (higher during rainy season)
            month = timestamp.month
            seasonal_factor = 1.0
            if month in [6, 7, 8, 9, 10, 11]:  # Rainy season in Philippines
                seasonal_factor = 1.5
            
            # Simulate daily patterns (higher during afternoon)
            hour = timestamp.hour
            daily_factor = 1.0 + 0.2 * np.sin((hour - 6) * np.pi / 12)
            
            # Base water level with random variation
            base_level = 25 + np.random.normal(0, 10)
            
            # Add trend (simulating rising water)
            trend = (i / num_samples) * 20
            
            # Calculate water level
            water_level = base_level * seasonal_factor * daily_factor + trend
            water_level = max(0, min(100, water_level))  # Clamp between 0-100
            
            # Determine flood status based on thresholds
            if water_level >= 75:
                status = 'Danger'
            elif water_level >= 60:
                status = 'Warning'
            elif water_level >= 45:
                status = 'Alert'
            else:
                status = 'Normal'
            
            data.append({
                'timestamp': timestamp,
                'water_level_cm': water_level,
                'status': status
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Generated {len(df)} data points")
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for machine learning.
        
        Args:
            df: Input DataFrame with water level data
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Time-based features
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # Sort by timestamp for rolling calculations
        df = df.sort_values('timestamp')
        
        # Rate of change (difference from previous reading)
        df['rate_of_change'] = df['water_level_cm'].diff().fillna(0)
        
        # Rolling averages
        df['avg_last_1h'] = df['water_level_cm'].rolling(window=12, min_periods=1).mean()  # Assuming 5-min intervals
        df['avg_last_6h'] = df['water_level_cm'].rolling(window=72, min_periods=1).mean()
        df['avg_last_24h'] = df['water_level_cm'].rolling(window=288, min_periods=1).mean()
        
        # Rolling max/min
        df['max_last_24h'] = df['water_level_cm'].rolling(window=288, min_periods=1).max()
        df['min_last_24h'] = df['water_level_cm'].rolling(window=288, min_periods=1).min()
        
        # Fill NaN values
        df = df.bfill().ffill()
        
        logger.info(f"Feature engineering complete. Features: {len(self.feature_columns)}")
        return df
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (X, y) arrays
        """
        logger.info("Preparing data for training...")
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Encode target variable
        y = self.label_encoder.fit_transform(df['status'])
        
        # Select features
        X = df[self.feature_columns].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        logger.info(f"Data prepared. X shape: {X.shape}, y shape: {y.shape}")
        return X, y
    
    def train(self, df: Optional[pd.DataFrame] = None, test_size: float = 0.2) -> Dict:
        """
        Train the flood prediction model.
        
        Args:
            df: Training data (if None, generates sample data)
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training {self.model_type} model...")
        
        # Generate sample data if not provided
        if df is None:
            logger.warning("No training data provided, generating sample data...")
            df = self.generate_sample_data(num_samples=1000)
        
        # Prepare data
        X, y = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Initialize model
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'decision_tree':
            self.model = DecisionTreeClassifier(
                max_depth=10,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        
        # Store metadata
        self.model_metadata = {
            'model_type': self.model_type,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_)),
            'trained_at': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        logger.info(f"Model trained successfully. Accuracy: {accuracy:.2f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        return self.model_metadata
    
    def predict(self, water_level: float, historical_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Predict flood risk for a given water level.
        
        Args:
            water_level: Current water level in cm
            historical_data: Historical data for feature calculation
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        logger.info(f"Predicting flood risk for water level: {water_level} cm")
        
        # Create feature vector
        current_time = datetime.now()
        
        if historical_data is not None and len(historical_data) > 0:
            # Calculate features from historical data
            df = historical_data.copy()
            df = df.append({'timestamp': current_time, 'water_level_cm': water_level}, ignore_index=True)
            df = self.engineer_features(df)
            features = df.iloc[-1][self.feature_columns].values.reshape(1, -1)
        else:
            # Use default values if no historical data
            features = np.array([[
                water_level,
                current_time.hour,
                current_time.weekday(),
                current_time.month,
                0,  # rate_of_change
                water_level,  # avg_last_1h
                water_level,  # avg_last_6h
                water_level,  # avg_last_24h
                water_level,  # max_last_24h
                water_level   # min_last_24h
            ]])
        
        # Scale features
        features = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        # Decode prediction
        predicted_status = self.label_encoder.inverse_transform([prediction])[0]
        
        # Determine severity
        severity_map = {
            'Normal': 'low',
            'Alert': 'medium',
            'Warning': 'high',
            'Danger': 'critical'
        }
        severity = severity_map.get(predicted_status, 'low')
        
        # Calculate confidence
        confidence = max(probabilities) * 100
        
        # Recommended action
        action_map = {
            'Normal': 'Continue monitoring',
            'Alert': 'Increase monitoring frequency',
            'Warning': 'Prepare for potential evacuation',
            'Danger': 'Initiate evacuation procedures'
        }
        recommended_action = action_map.get(predicted_status, 'Monitor')
        
        result = {
            'water_level_cm': water_level,
            'predicted_status': predicted_status,
            'flood_probability': confidence,
            'severity': severity,
            'alert_level': predicted_status,
            'confidence_score': confidence,
            'recommended_action': recommended_action,
            'probabilities': {
                status: prob for status, prob in zip(self.label_encoder.classes_, probabilities)
            },
            'timestamp': current_time.isoformat()
        }
        
        logger.info(f"Prediction: {predicted_status} (confidence: {confidence:.2f}%)")
        return result
    
    def save_model(self, filepath: str):
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        logger.info(f"Saving model to {filepath}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model and metadata
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'metadata': self.model_metadata
        }
        
        joblib.dump(model_data, filepath)
        logger.info("Model saved successfully")
    
    def load_model(self, filepath: str):
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to load the model from
        """
        logger.info(f"Loading model from {filepath}...")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_columns = model_data['feature_columns']
        self.model_metadata = model_data['metadata']
        self.is_trained = True
        
        logger.info("Model loaded successfully")
        logger.info(f"Model metadata: {self.model_metadata}")


# Example usage
if __name__ == "__main__":
    # Create and train model
    predictor = FloodPredictionModel(model_type='random_forest')
    
    # Train with sample data
    metrics = predictor.train()
    
    print("\n=== Training Metrics ===")
    print(f"Accuracy: {metrics['accuracy']:.2f}")
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"F1 Score: {metrics['f1_score']:.2f}")
    
    # Make predictions
    print("\n=== Sample Predictions ===")
    for level in [20, 40, 55, 70, 85]:
        result = predictor.predict(water_level=level)
        print(f"Water Level: {level}cm -> {result['predicted_status']} ({result['confidence_score']:.1f}% confidence)")
    
    # Save model
    model_path = "backend/ai/models/flood_prediction_model.pkl"
    predictor.save_model(model_path)
    print(f"\nModel saved to {model_path}")
