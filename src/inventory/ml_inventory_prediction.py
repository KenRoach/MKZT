from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet
from datetime import datetime, timedelta

class MLInventoryPredictor:
    def __init__(self):
        self.prophet_models = {}
        self.rf_model = RandomForestRegressor(n_estimators=100)
        
    async def predict_inventory_needs(self, restaurant_id: str) -> Dict[str, Any]:
        """Predict inventory needs using multiple ML models"""
        try:
            # Get historical data
            historical_data = await self._get_historical_data(restaurant_id)
            
            # Generate predictions using different models
            prophet_predictions = await self._prophet_predictions(historical_data)
            rf_predictions = await self._random_forest_predictions(historical_data)
            
            # Ensemble predictions
            final_predictions = await self._ensemble_predictions(
                prophet_predictions,
                rf_predictions
            )
            
            return {
                "status": "success",
                "predictions": final_predictions,
                "confidence_scores": await self._calculate_confidence_scores(
                    prophet_predictions,
                    rf_predictions
                )
            }
        except Exception as e:
            logger.error(f"Error predicting inventory: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _prophet_predictions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions using Prophet"""
        predictions = {}
        
        for item in data['items'].unique():
            if item not in self.prophet_models:
                self.prophet_models[item] = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=True
                )
                
            item_data = data[data['item'] == item]
            self.prophet_models[item].fit(item_data)
            
            future = self.prophet_models[item].make_future_dataframe(
                periods=14,  # 2 weeks forecast
                freq='D'
            )
            
            forecast = self.prophet_models[item].predict(future)
            predictions[item] = {
                'forecast': forecast['yhat'].values,
                'lower_bound': forecast['yhat_lower'].values,
                'upper_bound': forecast['yhat_upper'].values
            }
        
        return predictions

    async def _random_forest_predictions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions using Random Forest"""
        predictions = {}
        
        for item in data['items'].unique():
            item_data = data[data['item'] == item]
            
            # Prepare features
            features = self._prepare_rf_features(item_data)
            
            # Train model
            self.rf_model.fit(features, item_data['quantity'])
            
            # Generate predictions
            future_features = self._prepare_future_features(14)  # 2 weeks
            predictions[item] = self.rf_model.predict(future_features)
        
        return predictions

    async def _ensemble_predictions(self, prophet_pred: Dict[str, Any],
                                  rf_pred: Dict[str, Any]) -> Dict[str, Any]:
        """Combine predictions from different models"""
        ensemble_predictions = {}
        
        for item in prophet_pred.keys():
            # Weighted average of predictions
            ensemble_predictions[item] = {
                'forecast': 0.6 * prophet_pred[item]['forecast'] + 
                          0.4 * rf_pred[item],
                'confidence_interval': {
                    'lower': prophet_pred[item]['lower_bound'],
                    'upper': prophet_pred[item]['upper_bound']
                }
            }
        
        return ensemble_predictions 