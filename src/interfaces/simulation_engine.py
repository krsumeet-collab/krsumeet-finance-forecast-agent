"""Abstract interface for deterministic scenario simulation engines."""
from abc import ABC, abstractmethod
from src.models.schemas import WaterfallVarianceBridge, RiskClassEnum


class SimulationEngineInterface(ABC):
    @abstractmethod
    def compute_variance_waterfall(
        self,
        baseline_usd: float,
        risk_class: RiskClassEnum,
        custom_slippage_pct: float = None,
        cost_inflation_pct: float = 0.0,
    ) -> WaterfallVarianceBridge:
        """Compute exact deterministic variance waterfall and EBITDA impact."""
        pass
