"""BigQuery ML ARIMA-Plus & TimesFM Simulation Tool."""
from typing import Dict, Any, List
from src.interfaces.forecasting_engine import ForecastingEngineInterface
from src.models.schemas import RegionEnum, RiskClassEnum


class BigQueryMLForecastingTool(ForecastingEngineInterface):
    """Simulates Google Cloud BigQuery ML ARIMA_PLUS model and

    hosted Vertex AI TimesFM zero-shot foundation model endpoint.
    """

    BASELINES = {
        RegionEnum.EMEA: 90.90,   # $90.9M
        RegionEnum.LATAM: 52.00,  # $52.0M
        RegionEnum.NA: 145.00,    # $145.0M
        RegionEnum.APAC: 65.00,   # $65.0M
        RegionEnum.GLOBAL: 352.90,
    }

    CONFIDENCE_INTERVALS = {
        RegionEnum.EMEA: 1.80,
        RegionEnum.LATAM: 1.20,
        RegionEnum.NA: 2.50,
        RegionEnum.APAC: 1.50,
        RegionEnum.GLOBAL: 5.50,
    }

    async def predict_baseline(
        self, region: RegionEnum, horizon_days: int = 90
    ) -> Dict[str, Any]:
        """Runs BigQuery ML ARIMA-Plus baseline forecast over trailing 36-month ERP actuals."""
        base = self.BASELINES.get(region, 80.0)
        ci = self.CONFIDENCE_INTERVALS.get(region, 2.0)
        return {
            "model_type": "BIGQUERY_ML_ARIMA_PLUS",
            "region": region.value,
            "horizon_days": horizon_days,
            "baseline_revenue_usd": base,
            "confidence_interval_95": {
                "lower_bound_usd": round(base - ci, 2),
                "upper_bound_usd": round(base + ci, 2),
                "margin_error_usd": ci,
            },
            "seasonal_decomposition": {
                "trend": "MILD_DECELERATION",
                "quarterly_seasonality_factor": 1.04,
                "residual_variance": 0.012,
            },
        }

    async def run_forecast_simulation(
        self,
        region: RegionEnum,
        risk_summary: str,
        detected_root_causes: List[str],
    ) -> Dict[str, Any]:
        """Runs zero-shot TimesFM simulation adjusting assumptions based on detected risk triggers."""
        base = self.BASELINES.get(region, 80.0)
        ci = self.CONFIDENCE_INTERVALS.get(region, 2.0)

        # Causal Keyword Detection
        risk_text = (risk_summary + " " + " ".join(detected_root_causes)).lower()

        has_attrition = any(w in risk_text for w in ["resigned", "attrition", "departure", "vacancy", "departed", "leadership"])
        has_competitor = any(w in risk_text for w in ["competitor", "launch", "pricing", "rival", "disrupt", "neocloud", "alpha"])
        has_macro = any(w in risk_text for w in ["volatili", "headwind", "currency", "fx", "inflation", "tariff", "interest", "macro"])
        has_upside = any(w in risk_text for w in ["upside", "accel", "breakthrough", "expansion", "growth", "award"])
        is_stable = any(w in risk_text for w in ["stable", "routine", "cleanly", "normal"])

        if has_attrition and has_competitor:
            risk_class = RiskClassEnum.HIGH_RISK
            penalty_pct = 0.150  # 15% Variance Penalty
            risk_factor_explanation = (
                "High Risk (15% Variance Penalty) triggered by verified sales leadership "
                "attrition combined with aggressive competitor market entry."
            )
        elif has_upside and not has_macro and not has_attrition:
            risk_class = RiskClassEnum.UPSIDE_ACCELERATION
            penalty_pct = -0.080
            risk_factor_explanation = "Upside Acceleration (+8% expansion) driven by positive new product launch momentum."
        elif has_macro and not ("stable" in risk_text and "headwind" not in risk_text):
            risk_class = RiskClassEnum.MEDIUM_RISK
            penalty_pct = 0.080  # 8% Variance Penalty
            risk_factor_explanation = (
                "Medium Risk (8% Variance Penalty) triggered by regional macroeconomic and FX currency headwinds."
            )
        else:
            risk_class = RiskClassEnum.LOW_RISK
            penalty_pct = 0.020  # 2% Operational Variance
            risk_factor_explanation = "Low Risk (2% operational variance) under stable market conditions."

        variance_usd = round(base * penalty_pct, 3)
        simulated_revenue_usd = round(base - variance_usd, 3)

        return {
            "model_type": "VERTEX_AI_TIMESFM_200M",
            "region": region.value,
            "baseline_revenue_usd": base,
            "risk_class": risk_class,
            "variance_penalty_pct": penalty_pct,
            "projected_variance_miss_usd": variance_usd,
            "simulated_revenue_usd": simulated_revenue_usd,
            "confidence_interval_95": {
                "lower_bound_usd": round(simulated_revenue_usd - ci, 2),
                "upper_bound_usd": round(simulated_revenue_usd + ci, 2),
            },
            "risk_explanation": risk_factor_explanation,
        }


bigquery_ml_tool = BigQueryMLForecastingTool()
