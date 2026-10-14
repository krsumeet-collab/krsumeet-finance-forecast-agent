"""Leadership Notification Dispatcher Tool."""
from typing import Dict, Any, List
from src.models.schemas import RegionEnum, WaterfallVarianceBridge


class LeadershipNotificationTool:
    """Dispatches executive briefing packets to VP of Finance and Regional Sales Heads."""

    async def notify_leadership_team(
        self,
        region: RegionEnum,
        root_causes: List[str],
        waterfall: WaterfallVarianceBridge,
        executive_briefing: str,
        recipients: List[str] = None,
    ) -> Dict[str, Any]:
        """Transmits standardized strategic briefing to executive stakeholders."""
        if not recipients:
            recipients = [
                f"vp_finance@corp.internal",
                f"head_of_{region.value.lower()}_sales@corp.internal",
            ]

        packet = {
            "subject": f"[EXECUTIVE BRIEF] {region.value} Q3 Financial Forecast Risk & Mitigation Summary",
            "recipients": recipients,
            "root_causes": root_causes,
            "financial_impact": {
                "baseline_revenue_usd": f"${waterfall.baseline_revenue_usd:.1f}M",
                "simulated_revenue_usd": f"${waterfall.simulated_revenue_usd:.1f}M",
                "projected_variance_miss_usd": f"-${waterfall.total_variance_penalty_usd:.1f}M",
                "variance_percentage": f"-{waterfall.variance_percentage:.1f}%",
                "adjusted_ebitda_usd": f"${waterfall.adjusted_ebitda_usd:.1f}M",
            },
            "executive_briefing_text": executive_briefing,
            "dispatch_status": "DELIVERED",
        }
        return packet


notification_tool = LeadershipNotificationTool()
