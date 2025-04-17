from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class AnalyticsVisualization:
    def __init__(self):
        self.color_scheme = {
            'primary': '#2E86C1',
            'secondary': '#28B463',
            'accent': '#E74C3C',
            'neutral': '#85929E'
        }
        
    async def generate_dashboard_components(self, restaurant_id: str) -> Dict[str, Any]:
        """Generate all dashboard visualizations"""
        try:
            data = await self._fetch_analytics_data(restaurant_id)
            
            return {
                "sales_charts": await self._create_sales_visualizations(data),
                "performance_metrics": await self._create_performance_metrics(data),
                "customer_insights": await self._create_customer_insights(data),
                "inventory_analysis": await self._create_inventory_analysis(data),
                "predictive_charts": await self._create_predictive_charts(data)
            }
        except Exception as e:
            logger.error(f"Error generating dashboard: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _create_sales_visualizations(self, data: Dict) -> Dict[str, Any]:
        """Create sales-related visualizations"""
        # Revenue Timeline
        revenue_fig = go.Figure()
        revenue_fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        # Sales by Category
        category_fig = px.pie(
            data_frame=pd.DataFrame(data['category_sales']),
            values='amount',
            names='category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Hourly Sales Heatmap
        hourly_fig = go.Figure(data=go.Heatmap(
            z=data['hourly_sales_matrix'],
            x=data['hours'],
            y=data['days_of_week'],
            colorscale='Viridis'
        ))
        
        return {
            "revenue_timeline": revenue_fig.to_json(),
            "category_distribution": category_fig.to_json(),
            "hourly_heatmap": hourly_fig.to_json()
        }

    async def _create_performance_metrics(self, data: Dict) -> Dict[str, Any]:
        """Create performance metric visualizations"""
        # KPI Gauges
        kpi_figs = {}
        for metric in ['order_completion_rate', 'customer_satisfaction', 'kitchen_efficiency']:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = data[f'{metric}_value'],
                gauge = {'axis': {'range': [0, 100]},
                        'bar': {'color': self.color_scheme['primary']}},
                title = {'text': metric.replace('_', ' ').title()}
            ))
            kpi_figs[metric] = fig.to_json()
        
        return kpi_figs

    async def _create_predictive_charts(self, data: Dict) -> Dict[str, Any]:
        """Create predictive analysis visualizations"""
        # Demand Forecast
        forecast_fig = go.Figure()
        forecast_fig.add_trace(go.Scatter(
            x=data['forecast_dates'],
            y=data['forecast_values'],
            mode='lines',
            name='Forecast',
            line=dict(color=self.color_scheme['primary'])
        ))
        forecast_fig.add_trace(go.Scatter(
            x=data['forecast_dates'],
            y=data['confidence_upper'],
            fill=None,
            mode='lines',
            line=dict(color=self.color_scheme['neutral'], width=0),
            showlegend=False
        ))
        forecast_fig.add_trace(go.Scatter(
            x=data['forecast_dates'],
            y=data['confidence_lower'],
            fill='tonexty',
            mode='lines',
            line=dict(color=self.color_scheme['neutral'], width=0),
            name='Confidence Interval'
        ))
        
        return {
            "demand_forecast": forecast_fig.to_json(),
            "prediction_metrics": data['prediction_metrics']
        } 