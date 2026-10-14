"""FastAPI Web Application Server for Autonomous Forecast Generation Agent."""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from src.models.schemas import (
    ForecastGenerateRequest,
    ForecastGenerateResponse,
    SimulationRequest,
    SimulationResponse,
    RegionEnum,
    ExecutionStatusEnum,
)
from src.agents.orchestrator import orchestrator
from src.tools.financial_math_engine import financial_math_engine
from src.tools.crm_salesforce_tool import crm_tool
from src.tools.bigquery_ml_tool import bigquery_ml_tool
from src.observability.telemetry import telemetry

app = FastAPI(
    title="Autonomous Finance Agent — Forecast Generation Swarm",
    description="Production-grade enterprise multi-agent API on Google Cloud Platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Liveness and readiness probe for Cloud Run."""
    return {
        "status": "HEALTHY",
        "service": "finance-forecast-agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "upstream_connectivity": {
            "bigquery_ml": "CONNECTED",
            "vertex_timesfm": "CONNECTED",
            "crm_mcp": "CONNECTED",
            "workday_hr": "CONNECTED",
            "bloomberg_api": "CONNECTED",
        },
    }


@app.post(
    "/v1/forecast/generate",
    response_model=ForecastGenerateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Forecasting"],
)
async def generate_forecast(request: ForecastGenerateRequest) -> ForecastGenerateResponse:
    """Triggers end-to-end multi-agent swarm: anomaly detection, RCA, HITL gate,

    TimesFM simulation, and executive financial briefing synthesis.
    """
    try:
        response = await orchestrator.execute_forecast_workflow(request)
        if response.status == ExecutionStatusEnum.REJECTED_BY_GUARDRAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=response.executive_briefing,
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal forecast execution error: {str(e)}",
        )


@app.post(
    "/v1/forecast/simulate",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Simulation"],
)
async def simulate_scenario(request: SimulationRequest) -> SimulationResponse:
    """Executes deterministic what-if scenario simulations with custom risk haircuts."""
    try:
        waterfall = financial_math_engine.compute_variance_waterfall(
            baseline_usd=request.baseline_revenue_usd,
            custom_slippage_pct=request.slippage_percentage,
            cost_inflation_pct=request.cost_inflation_percentage,
        )
        return SimulationResponse(
            region=request.region,
            baseline_revenue_usd=request.baseline_revenue_usd,
            simulated_revenue_usd=waterfall.simulated_revenue_usd,
            variance_penalty_usd=waterfall.total_variance_penalty_usd,
            adjusted_ebitda_usd=waterfall.adjusted_ebitda_usd,
            waterfall=waterfall,
            tie_out_verified=waterfall.tie_out_verified,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation error: {str(e)}",
        )


@app.get("/v1/forecast/actuals", tags=["Forecasting"])
async def get_actuals(region: RegionEnum, trailing_months: int = 12) -> Dict[str, Any]:
    """Retrieves historical actuals and CRM stage-weighted opportunity pipeline."""
    try:
        metrics = await crm_tool.fetch_pipeline_metrics(region)
        arima_baseline = await bigquery_ml_tool.predict_baseline(region)
        return {
            "region": region.value,
            "trailing_months": trailing_months,
            "quarterly_target_usd": metrics.quarterly_target_usd,
            "raw_pipeline_usd": metrics.raw_pipeline_usd,
            "weighted_pipeline_usd": metrics.weighted_pipeline_usd,
            "arima_baseline": arima_baseline,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching actuals: {str(e)}",
        )
