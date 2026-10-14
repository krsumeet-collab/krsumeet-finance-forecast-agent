"""Salesforce CRM & BI Pipeline Ingestion Tool."""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from src.models.schemas import PipelineMetrics, RegionEnum, PipelineOpportunity, SalesActivityFinding


class SalesforceCRMTool:
    """Simulates Salesforce Model Context Protocol (MCP) tool server

    and Looker BI metric integration.
    """

    REGIONAL_TARGETS = {
        RegionEnum.EMEA: 105.0,  # $105M
        RegionEnum.LATAM: 60.0,  # $60M
        RegionEnum.NA: 150.0,    # $150M
        RegionEnum.APAC: 75.0,   # $75M
        RegionEnum.GLOBAL: 390.0,
    }

    async def fetch_pipeline_metrics(self, region: RegionEnum) -> PipelineMetrics:
        """Calls BI Platform (Looker) & BigQuery history to assess performance vs plan."""
        target = self.REGIONAL_TARGETS.get(region, 100.0)

        if region == RegionEnum.EMEA:
            # 15% drop below target threshold, 2-week continuous decline
            raw_pipeline = 120.0
            weighted_pipeline = 48.0
            drop_pct = 15.0
            is_anomalous = True
            summary = (
                "EMEA region new bookings have dropped 15.0% below the target threshold ($105.0M plan vs "
                "$90.9M projected baseline). BigQuery historical trend confirms a sustained two-week decline."
            )
        elif region == RegionEnum.LATAM:
            raw_pipeline = 69.0
            weighted_pipeline = 31.2
            drop_pct = 8.0
            is_anomalous = True
            summary = "LATAM region pacing 8.0% below quarterly plan due to currency headwinds and FX volatility."
        elif region == RegionEnum.NA:
            raw_pipeline = 162.0
            weighted_pipeline = 87.0
            drop_pct = 2.0
            is_anomalous = False
            summary = "NA region tracking healthy with minor normal 2.0% operational variance against $150.0M plan."
        else:
            raw_pipeline = 90.0
            weighted_pipeline = 45.0
            drop_pct = 3.0
            is_anomalous = False
            summary = f"{region.value} tracking within normal operational thresholds."

        return PipelineMetrics(
            region=region,
            quarterly_target_usd=target,
            raw_pipeline_usd=raw_pipeline,
            weighted_pipeline_usd=weighted_pipeline,
            baseline_drop_pct=drop_pct,
            is_anomalous=is_anomalous,
            summary=summary,
        )

    async def get_team_performance_data(self, region: RegionEnum) -> List[str]:
        """Isolates pipeline drops to specific sales territories."""
        if region == RegionEnum.EMEA:
            return ["EMEA-SOUTH-1", "EMEA-CENTRAL-2"]
        elif region == RegionEnum.LATAM:
            return ["LATAM-BRAZIL-1", "LATAM-ANDES-2"]
        elif region == RegionEnum.APAC:
            return ["APAC-JAPAN-1"]
        else:
            return ["NA-EAST-1"]

    async def analyze_crm_activity_logs(
        self, region: RegionEnum, territories: List[str], prompt_context: str = ""
    ) -> Dict[str, Any]:
        """Parses CRM deal comments and meeting notes for designated territories using NLP."""
        ctx = (prompt_context or "").lower()

        # Check for known leadership names in context
        leaders = [
            "marcus vance", "elena rostova", "julian moreau", "kenji sato",
            "priya sharma", "david reynolds", "sarah jenkins", "carlos mendoza",
            "astrid lindholm", "wei zhang", "michael chang", "mateo silva"
        ]
        flagged_leader = None
        for leader in leaders:
            if leader in ctx:
                flagged_leader = leader.title()
                break

        if not flagged_leader and ("leadership" in ctx or "attrition" in ctx or "resigned" in ctx):
            if region == RegionEnum.EMEA:
                flagged_leader = "Marcus Vance"
            elif region == RegionEnum.APAC:
                flagged_leader = "Kenji Sato"
            elif region == RegionEnum.LATAM:
                flagged_leader = "Carlos Mendoza"
            else:
                flagged_leader = "David Reynolds"
        elif not flagged_leader and region == RegionEnum.EMEA and "stable" not in ctx and "stabili" not in ctx and "upside" not in ctx and "macro" not in ctx and "fx" not in ctx and "currency" not in ctx:
            flagged_leader = "Marcus Vance"

        if flagged_leader:
            return {
                "stalled_deals_count": 14,
                "unattended_pipeline_usd": 18500000.00,
                "dominant_topic": "LEADERSHIP_VACANCY",
                "extracted_notes": [
                    f"Client VP of Engineering requested executive sponsorship; deal stalled pending {flagged_leader} replacement.",
                    f"Pricing concessions awaiting director sign-off; {flagged_leader} departed company recently.",
                    "Renewal RFP delayed by procurement; lacks regional director signature.",
                ],
                "flagged_employee_name": flagged_leader,
                "flagged_employee_id": "EMP-94821",
                "summary": f"Repeated CRM deal comments cite stalled decisions following the departure of Sales Director {flagged_leader}.",
            }
        elif (
            "fx" in ctx
            or "currency" in ctx
            or "volatili" in ctx
            or "inflation" in ctx
            or "interest" in ctx
            or "tax" in ctx
            or "macro" in ctx
            or "indicator" in ctx
            or (region == RegionEnum.LATAM and "leadership" not in ctx and "attrition" not in ctx)
        ) and "stable" not in ctx and "stabili" not in ctx and "upside" not in ctx:
            return {
                "stalled_deals_count": 6,
                "unattended_pipeline_usd": 4200000.00,
                "dominant_topic": "CURRENCY_VOLATILITY",
                "extracted_notes": ["Client requested contract re-denomination into local currency."],
                "flagged_employee_name": None,
                "flagged_employee_id": None,
                "summary": "CRM activity logs identify deal delays tied to foreign exchange volatility and contract re-negotiations.",
            }
        elif "upside" in ctx or "launch" in ctx or "accel" in ctx or "breakthrough" in ctx:
            return {
                "stalled_deals_count": 0,
                "unattended_pipeline_usd": 0.0,
                "dominant_topic": "PIPELINE_ACCELERATION",
                "extracted_notes": ["New product trial conversions tracking 3x historical velocity."],
                "flagged_employee_name": None,
                "flagged_employee_id": None,
                "summary": "CRM activity shows rapid expansion and strong deal acceleration driven by new product demand.",
            }
        else:
            return {
                "stalled_deals_count": 2,
                "unattended_pipeline_usd": 800000.00,
                "dominant_topic": "ROUTINE_SALES_CYCLE",
                "extracted_notes": ["Standard contract redlining with corporate legal."],
                "flagged_employee_name": None,
                "flagged_employee_id": None,
                "summary": "Routine transaction cycles progressing cleanly with normal stage progression.",
            }


crm_tool = SalesforceCRMTool()
