"""Compatibility package alias for forecast_generation_agent as defined in capstone architecture specification."""
from src.agents.orchestrator import MasterForecastOrchestrator, orchestrator
from src.api.app import app

__all__ = ["MasterForecastOrchestrator", "orchestrator", "app"]
