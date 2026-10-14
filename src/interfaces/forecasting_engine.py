"""Abstract interface for time-series forecasting engines."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class ForecastingEngineInterface(ABC):
    @abstractmethod
    async def predict_baseline(self, region: str, horizon_days: int = 90) -> Dict[str, Any]:
        """Generate statistical baseline forecast with 95% confidence intervals."""
        pass
