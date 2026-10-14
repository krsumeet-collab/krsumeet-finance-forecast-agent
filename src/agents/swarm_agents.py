"""Specialized Swarm Sub-Agents for A2A Autonomous Financial Forecasting.

Encapsulated as Python function wrappers to decouple root LLM prompt complexity.
"""
from typing import Dict, Any, List
from src.models.schemas import (
    RegionEnum,
    PipelineMetrics,
    SalesActivityFinding,
    MarketIntelligenceFinding,
    WaterfallVarianceBridge,
    RiskClassEnum,
)
from src.tools.crm_salesforce_tool import crm_tool
from src.tools.workday_hr_tool import workday_tool
from src.tools.bloomberg_market_tool import bloomberg_tool
from src.tools.bigquery_ml_tool import bigquery_ml_tool
from src.tools.financial_math_engine import financial_math_engine
from src.tools.notification_tool import notification_tool
from src.observability.telemetry import telemetry


async def trigger_pipeline_monitor(region: RegionEnum) -> PipelineMetrics:
    """Sub-Agent 1: Fetches regional operational metrics from Looker KPI & BigQuery historical trends."""
    async with telemetry.start_span("agent_pipeline_monitor", {"region": region.value}):
        metrics = await crm_tool.fetch_pipeline_metrics(region)
        return metrics


async def investigate_internal_sales(region: RegionEnum, prompt_context: str = "") -> Dict[str, Any]:
    """Sub-Agent 2: Diagnoses internal sales bottlenecks via Salesforce activity logs and Workday HR status."""
    async with telemetry.start_span("agent_sales_activity", {"region": region.value}):
        # Step A: Isolate territories
        territories = await crm_tool.get_team_performance_data(region)

        # Step B: Parse CRM activity logs and deal notes
        crm_logs = await crm_tool.analyze_crm_activity_logs(region, territories, prompt_context)

        # Step C: Query Workday HR if employee name flagged
        hr_status = None
        root_cause_tag = "Routine Operational Pacing"
        if crm_logs.get("flagged_employee_name"):
            hr_status = await workday_tool.get_employee_status(
                employee_name=crm_logs["flagged_employee_name"]
            )
            if hr_status.resigned:
                root_cause_tag = f"Unexpected Team Lead Attrition ({hr_status.full_name}, {hr_status.role_title})"

        return {
            "sub_agent": "SalesActivityAgent",
            "region": region.value,
            "territories_isolated": territories,
            "stalled_deals_count": crm_logs["stalled_deals_count"],
            "unattended_pipeline_usd": crm_logs["unattended_pipeline_usd"],
            "employee_status": hr_status.model_dump() if hr_status else None,
            "root_cause_tag": root_cause_tag,
            "diagnostic_summary": crm_logs["summary"],
        }


async def investigate_external_market(region: RegionEnum, prompt_context: str = "") -> Dict[str, Any]:
    """Sub-Agent 3: Identifies external regional factors/risks using Bloomberg market news feeds."""
    async with telemetry.start_span("agent_market_intelligence", {"region": region.value}):
        market_intel = await bloomberg_tool.scan_market_news_feeds(region, prompt_context)

        root_cause_tag = "Normal Market Conditions"
        if market_intel.key_competitors_active:
            root_cause_tag = f"New Competitive Product Launch ({', '.join(market_intel.key_competitors_active)})"
        elif market_intel.macro_headwinds:
            root_cause_tag = f"Macroeconomic Headwinds ({', '.join(market_intel.macro_headwinds)})"

        return {
            "sub_agent": "MarketIntelligenceAgent",
            "region": region.value,
            "key_competitors": market_intel.key_competitors_active,
            "macro_headwinds": market_intel.macro_headwinds,
            "root_cause_tag": root_cause_tag,
            "news_summary": market_intel.finding_summary,
        }


async def generate_forecast_impact(
    region: RegionEnum,
    risk_summary: str,
    root_causes: List[str],
) -> Dict[str, Any]:
    """Sub-Agent 4: Computes time-series predictions via TimesFM and deterministic financial variance waterfall."""
    async with telemetry.start_span("agent_forecast_generation", {"region": region.value}):
        # 1. TimesFM statistical simulation
        sim_result = await bigquery_ml_tool.run_forecast_simulation(
            region=region,
            risk_summary=risk_summary,
            detected_root_causes=root_causes,
        )

        # 2. Deterministic mathematical waterfall
        waterfall = financial_math_engine.compute_variance_waterfall(
            baseline_usd=sim_result["baseline_revenue_usd"],
            risk_class=sim_result["risk_class"],
            custom_slippage_pct=sim_result["variance_penalty_pct"],
        )

        return {
            "model_type": sim_result["model_type"],
            "baseline_revenue_usd": sim_result["baseline_revenue_usd"],
            "simulated_revenue_usd": sim_result["simulated_revenue_usd"],
            "projected_variance_usd": sim_result["projected_variance_miss_usd"],
            "risk_class": sim_result["risk_class"],
            "confidence_interval_95": sim_result["confidence_interval_95"],
            "risk_explanation": sim_result["risk_explanation"],
            "waterfall_bridge": waterfall,
        }


async def notify_leadership_team(
    region: RegionEnum,
    root_causes: List[str],
    waterfall: WaterfallVarianceBridge,
    executive_briefing: str,
) -> Dict[str, Any]:
    """Sub-Agent 5: Formats and transmits executive packets to leadership."""
    async with telemetry.start_span("agent_leadership_notification", {"region": region.value}):
        dispatch_result = await notification_tool.notify_leadership_team(
            region=region,
            root_causes=root_causes,
            waterfall=waterfall,
            executive_briefing=executive_briefing,
        )
        return dispatch_result
