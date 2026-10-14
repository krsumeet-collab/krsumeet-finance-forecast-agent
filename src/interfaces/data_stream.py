"""Abstract interface definitions for FP&A multi-agent swarm."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.models.schemas import PipelineMetrics, EmployeeStatus, MarketIntelligenceFinding


class DataStreamInterface(ABC):
    @abstractmethod
    async def fetch_pipeline_metrics(self, region: str) -> PipelineMetrics:
        """Fetch CRM opportunities and stage-weighted pipeline metrics."""
        pass

    @abstractmethod
    async def fetch_crm_activity_logs(self, region: str, territory_id: str) -> List[Dict[str, Any]]:
        """Fetch and analyze CRM opportunity stage notes."""
        pass

    @abstractmethod
    async def check_employee_status(self, employee_id: str) -> EmployeeStatus:
        """Query HR information system for employee employment status."""
        pass

    @abstractmethod
    async def scan_market_news(self, region: str, sector: str) -> MarketIntelligenceFinding:
        """Query market intelligence news feeds for competitor and macroeconomic triggers."""
        pass
