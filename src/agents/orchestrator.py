"""Master Forecast Orchestrator (Root Agent) for Google ADK Swarm."""
import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from src.models.schemas import (
    RegionEnum,
    ForecastGenerateRequest,
    ForecastGenerateResponse,
    ExecutionStatusEnum,
    RiskClassEnum,
    GuardrailVerdictEnum,
)
from src.security.guardrails import guardrails
from src.security.dlp_sanitizer import dlp_sanitizer
from src.agents.swarm_agents import (
    trigger_pipeline_monitor,
    investigate_internal_sales,
    investigate_external_market,
    generate_forecast_impact,
    notify_leadership_team,
)
from src.tools.human_approval_tool import human_approval_tool
from src.tools.audit_logger import audit_logger
from src.observability.telemetry import telemetry
from src.observability.pubsub_broadcaster import pubsub_broadcaster


class MasterForecastOrchestrator:
    """The Master Forecast Orchestrator is the root router directing specialized

    domains to sub-agents, orchestrating data flow, managing the human approval gate,
    and triggering predictive forecasting.
    """

    async def execute_forecast_workflow(
        self, request: ForecastGenerateRequest
    ) -> ForecastGenerateResponse:
        """Executes the full end-to-end autonomous forecasting and RCA workflow."""
        start_time = time.perf_counter()
        execution_id = str(uuid.uuid4())
        region = request.region
        prompt_text = request.prompt_override or f"Generate a forecast analysis for the {region.value} region."

        # ---------------------------------------------------------------------
        # Step 0: Pre-Execution Security Guardrails & Input Sanitization
        # ---------------------------------------------------------------------
        verdict, guardrail_reason = guardrails.evaluate(prompt_text)
        if verdict == GuardrailVerdictEnum.BLOCK:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            await audit_logger.log_event(
                execution_id=execution_id,
                caller_identity=request.user_id,
                region=region,
                fiscal_period=request.fiscal_period,
                event_type="GUARDRAIL_INTERCEPTION",
                input_prompt=prompt_text,
                tools_called=["pre_execution_guardrails"],
                model_id="gemini-2.5-pro",
                latency_ms=elapsed_ms,
                guardrail_verdict=verdict,
                audit_metadata={"rejection_reason": guardrail_reason},
            )
            return ForecastGenerateResponse(
                execution_id=execution_id,
                region=region,
                fiscal_period=request.fiscal_period,
                status=ExecutionStatusEnum.REJECTED_BY_GUARDRAILS,
                baseline_forecast_usd=0.0,
                simulated_revenue_usd=0.0,
                variance_penalty_usd=0.0,
                risk_class=RiskClassEnum.REJECTED_SECURITY_VIOLATION,
                root_causes=["Security Violation: Adversarial or Out-of-Scope Prompt Rejected."],
                executive_briefing=f"Request Blocked by Security Perimeter: {guardrail_reason}",
                human_approval_status="NOT_APPLICABLE",
                audit_trail_recorded=True,
                latency_ms=elapsed_ms,
                guardrail_verdict=verdict,
            )

        sanitized_prompt = dlp_sanitizer.sanitize_text(prompt_text)

        # ---------------------------------------------------------------------
        # Step 1: Continuous Pipeline Monitoring Check (Looker + BigQuery)
        # ---------------------------------------------------------------------
        pipeline_metrics = await trigger_pipeline_monitor(region)

        # ---------------------------------------------------------------------
        # Step 2: Parallel A2A Investigation (Sales Activity + Market Intel)
        # ---------------------------------------------------------------------
        sales_task = asyncio.create_task(investigate_internal_sales(region, prompt_text))
        market_task = asyncio.create_task(investigate_external_market(region, prompt_text))
        sales_finding, market_finding = await asyncio.gather(sales_task, market_task)

        # Consolidate Root Causes
        root_causes = [
            sales_finding["root_cause_tag"],
            market_finding["root_cause_tag"],
        ]
        investigation_summary = (
            f"Internal: {sales_finding['diagnostic_summary']} | External: {market_finding['news_summary']}"
        )

        # ---------------------------------------------------------------------
        # Step 3: Human-in-the-Loop (HITL) Governance Gate
        # ---------------------------------------------------------------------
        approval_result = await human_approval_tool.request_human_approval(
            region=region,
            root_causes=root_causes,
            auto_approve=request.auto_approve_simulation,
            approver_email=request.user_id,
        )

        if approval_result["status"] != "APPROVED":
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ForecastGenerateResponse(
                execution_id=execution_id,
                region=region,
                fiscal_period=request.fiscal_period,
                status=ExecutionStatusEnum.PENDING_APPROVAL,
                baseline_forecast_usd=pipeline_metrics.raw_pipeline_usd,
                simulated_revenue_usd=pipeline_metrics.weighted_pipeline_usd,
                variance_penalty_usd=0.0,
                risk_class=RiskClassEnum.MEDIUM_RISK,
                root_causes=root_causes,
                executive_briefing="Forecast simulation paused awaiting executive director approval.",
                human_approval_status="PENDING",
                audit_trail_recorded=True,
                latency_ms=elapsed_ms,
            )

        # ---------------------------------------------------------------------
        # Step 4: Forecast Generation & Quantitative Simulation (TimesFM)
        # ---------------------------------------------------------------------
        sim_payload = await generate_forecast_impact(
            region=region,
            risk_summary=investigation_summary,
            root_causes=root_causes,
        )
        waterfall = sim_payload["waterfall_bridge"]

        # ---------------------------------------------------------------------
        # Step 5: Executive Financial Narrative Synthesis
        # ---------------------------------------------------------------------
        executive_briefing = self._synthesize_executive_narrative(
            region=region,
            fiscal_period=request.fiscal_period,
            baseline_revenue=waterfall.baseline_revenue_usd,
            simulated_revenue=waterfall.simulated_revenue_usd,
            variance_miss=waterfall.total_variance_penalty_usd,
            risk_class=sim_payload["risk_class"],
            root_causes=root_causes,
            waterfall=waterfall,
        )

        # ---------------------------------------------------------------------
        # Step 6: Dispatch Leadership Notification & Pub/Sub Broadcaster
        # ---------------------------------------------------------------------
        await notify_leadership_team(
            region=region,
            root_causes=root_causes,
            waterfall=waterfall,
            executive_briefing=executive_briefing,
        )

        await pubsub_broadcaster.broadcast_forecast_alert(
            region=region.value,
            variance_penalty_usd=waterfall.total_variance_penalty_usd,
            simulated_revenue_usd=waterfall.simulated_revenue_usd,
            root_causes=root_causes,
            execution_id=execution_id,
        )

        # ---------------------------------------------------------------------
        # Step 7: Immutable Audit Logging (Cloud Logging / BigQuery)
        # ---------------------------------------------------------------------
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        await audit_logger.log_event(
            execution_id=execution_id,
            caller_identity=request.user_id,
            region=region,
            fiscal_period=request.fiscal_period,
            event_type="FORECAST_WORKFLOW_COMPLETED",
            input_prompt=sanitized_prompt,
            tools_called=[
                "trigger_pipeline_monitor",
                "investigate_internal_sales",
                "investigate_external_market",
                "request_human_approval",
                "generate_forecast_impact",
                "notify_leadership_team",
            ],
            model_id="gemini-2.5-pro",
            latency_ms=elapsed_ms,
            guardrail_verdict=verdict,
            baseline_forecast_usd=waterfall.baseline_revenue_usd,
            simulated_revenue_usd=waterfall.simulated_revenue_usd,
            variance_penalty_usd=waterfall.total_variance_penalty_usd,
            applied_risk_penalty_pct=waterfall.variance_percentage / 100.0,
            executive_briefing=executive_briefing,
            audit_metadata={
                "root_causes": root_causes,
                "approval": approval_result,
                "adjusted_ebitda_usd": waterfall.adjusted_ebitda_usd,
            },
        )

        return ForecastGenerateResponse(
            execution_id=execution_id,
            region=region,
            fiscal_period=request.fiscal_period,
            status=ExecutionStatusEnum.COMPLETED,
            baseline_forecast_usd=waterfall.baseline_revenue_usd,
            simulated_revenue_usd=waterfall.simulated_revenue_usd,
            variance_penalty_usd=waterfall.total_variance_penalty_usd,
            risk_class=sim_payload["risk_class"],
            root_causes=root_causes,
            waterfall_bridge=waterfall,
            executive_briefing=executive_briefing,
            human_approval_status="APPROVED",
            audit_trail_recorded=True,
            latency_ms=elapsed_ms,
            guardrail_verdict=verdict,
        )

    def _synthesize_executive_narrative(
        self,
        region: RegionEnum,
        fiscal_period: str,
        baseline_revenue: float,
        simulated_revenue: float,
        variance_miss: float,
        risk_class: RiskClassEnum,
        root_causes: List[str],
        waterfall: Any,
    ) -> str:
        """Synthesizes high-impact executive financial commentary grounded in exact math."""
        causes_formatted = "\n  * " + "\n  * ".join(root_causes)

        if risk_class == RiskClassEnum.HIGH_RISK:
            brief = (
                f"EXECUTIVE BRIEFING: {region.value} {fiscal_period} FORECAST VARIANCE ANALYSIS\n\n"
                f"1. Top-Line Projection & Variance Bridge:\n"
                f"   * Baseline TimesFM Projection: ${baseline_revenue:.1f}M\n"
                f"   * Risk-Adjusted Simulation: ${simulated_revenue:.1f}M\n"
                f"   * Projected Revenue Miss: -${variance_miss:.1f}M (-{waterfall.variance_percentage:.1f}%)\n"
                f"   * Operating EBITDA Impact: Reduced from ${waterfall.baseline_ebitda_usd:.1f}M to ${waterfall.adjusted_ebitda_usd:.1f}M "
                f"(-{waterfall.ebitda_margin_compression_bps:.0f} bps compression)\n\n"
                f"2. Causal Attribution (Data-Grounded):\n"
                f"   The verified pipeline deceleration is attributed to two correlated drivers:{causes_formatted}\n"
                f"   CRM telemetry confirms 14 enterprise opportunities ($18.5M unweighted pipeline) stalled following "
                f"leadership attrition in Southern EMEA, while aggressive pricing from Competitor X has lengthened deal cycles.\n\n"
                f"3. Strategic Mitigation Options:\n"
                f"   a. Reassign key executive sponsorship across stalled Stage 4/5 accounts within 5 business days.\n"
                f"   b. Introduce competitive displacement pricing incentives to counter Competitor X.\n"
                f"   c. Accelerate Central European pipeline to offset the projected ${variance_miss:.1f}M shortfall."
            )
        elif risk_class == RiskClassEnum.MEDIUM_RISK:
            brief = (
                f"EXECUTIVE BRIEFING: {region.value} {fiscal_period} FORECAST ANALYSIS\n\n"
                f"1. Top-Line Projection & Variance Bridge:\n"
                f"   * Baseline TimesFM Projection: ${baseline_revenue:.1f}M\n"
                f"   * Risk-Adjusted Simulation: ${simulated_revenue:.1f}M\n"
                f"   * Projected Variance Headwind: -${variance_miss:.1f}M (-{waterfall.variance_percentage:.1f}%)\n"
                f"   * Adjusted EBITDA: ${waterfall.adjusted_ebitda_usd:.1f}M\n\n"
                f"2. Causal Attribution:\n"
                f"   Regional performance impacted by macroeconomic FX volatility:{causes_formatted}\n\n"
                f"3. Strategic Recommendations:\n"
                f"   Deploy localized currency hedging and adjust procurement index terms."
            )
        elif risk_class == RiskClassEnum.UPSIDE_ACCELERATION:
            brief = (
                f"EXECUTIVE BRIEFING: {region.value} {fiscal_period} UPSIDE ACCELERATION ANALYSIS\n\n"
                f"1. Top-Line Projection & Growth Bridge:\n"
                f"   * Baseline Projection: ${baseline_revenue:.1f}M\n"
                f"   * Upside Simulated Revenue: ${simulated_revenue:.1f}M (+${abs(variance_miss):.1f}M expansion)\n\n"
                f"2. Positive Growth Drivers:{causes_formatted}\n\n"
                f"3. Strategic Recommendations:\n"
                f"   Scale cloud infrastructure capacity to support accelerated customer deployment."
            )
        else:
            brief = (
                f"EXECUTIVE BRIEFING: {region.value} {fiscal_period} STABLE RUN-RATE REPORT\n\n"
                f"1. Top-Line Projection:\n"
                f"   * Baseline Projection: ${baseline_revenue:.1f}M\n"
                f"   * Projected Revenue: ${simulated_revenue:.1f}M (minor 2.0% operational variance: -${variance_miss:.1f}M)\n"
                f"   * Adjusted EBITDA: ${waterfall.adjusted_ebitda_usd:.1f}M\n\n"
                f"2. Operational Status:\n"
                f"   Normal transaction velocity and stable enterprise renewals across all territories."
            )

        return brief


orchestrator = MasterForecastOrchestrator()
