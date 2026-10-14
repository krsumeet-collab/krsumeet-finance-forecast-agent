"""Pydantic v2 Data Models and Schemas for Autonomous Finance Swarm."""
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RegionEnum(str, Enum):
    EMEA = "EMEA"
    LATAM = "LATAM"
    NA = "NA"
    APAC = "APAC"
    GLOBAL = "GLOBAL"


class RiskClassEnum(str, Enum):
    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_RISK = "LOW_RISK"
    UPSIDE_ACCELERATION = "UPSIDE_ACCELERATION"
    REJECTED_SECURITY_VIOLATION = "REJECTED_SECURITY_VIOLATION"


class ExecutionStatusEnum(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    REJECTED_BY_GUARDRAILS = "REJECTED_BY_GUARDRAILS"
    FAILED = "FAILED"


class GuardrailVerdictEnum(str, Enum):
    PERMIT = "PERMIT"
    SANITIZE = "SANITIZE"
    BLOCK = "BLOCK"


class PipelineOpportunity(BaseModel):
    model_config = ConfigDict(extra="ignore")

    opportunity_id: str
    account_id: str
    deal_name: str
    region: RegionEnum
    territory_id: str
    stage_name: str
    probability: float = Field(ge=0.0, le=1.0)
    amount_usd: float = Field(ge=0.0)
    weighted_amount_usd: float = Field(ge=0.0)
    expected_close_date: date
    is_stalled: bool = False
    last_activity_date: datetime


class PipelineMetrics(BaseModel):
    region: RegionEnum
    quarterly_target_usd: float
    raw_pipeline_usd: float
    weighted_pipeline_usd: float
    baseline_drop_pct: float
    is_anomalous: bool
    summary: str


class EmployeeStatus(BaseModel):
    employee_id: str
    full_name: str
    role_title: str
    region: RegionEnum
    territory: str
    is_active: bool
    resigned: bool
    resignation_date: Optional[date] = None
    days_since_resignation: Optional[int] = None


class SalesActivityFinding(BaseModel):
    territories_isolated: List[str]
    stalled_deals_count: int
    unattended_pipeline_usd: float
    identified_leader_attrition: Optional[EmployeeStatus] = None
    finding_summary: str


class MarketNewsItem(BaseModel):
    headline: str
    source: str
    published_date: str
    relevance_score: float
    key_competitor: Optional[str] = None
    sentiment: str  # NEGATIVE, NEUTRAL, POSITIVE


class MarketIntelligenceFinding(BaseModel):
    key_competitors_active: List[str]
    news_items: List[MarketNewsItem]
    macro_headwinds: List[str]
    finding_summary: str


class WaterfallVarianceBridge(BaseModel):
    baseline_revenue_usd: float
    slippage_haircut_usd: float
    competitor_or_macro_impact_usd: float
    total_variance_penalty_usd: float
    simulated_revenue_usd: float
    variance_percentage: float
    baseline_ebitda_usd: float
    adjusted_ebitda_usd: float
    ebitda_margin_compression_bps: float
    tie_out_verified: bool = True


class ForecastGenerateRequest(BaseModel):
    region: RegionEnum = Field(default=RegionEnum.EMEA)
    fiscal_period: str = Field(default="Q3_2026", pattern=r"^Q[1-4]_[0-9]{4}$")
    prompt_override: Optional[str] = None
    auto_approve_simulation: bool = Field(
        default=False,
        description="Bypasses interactive chat wait for testing/batch runs."
    )
    user_id: str = Field(default="director_fpa@corp.internal")


class ForecastGenerateResponse(BaseModel):
    execution_id: str
    region: RegionEnum
    fiscal_period: str
    status: ExecutionStatusEnum
    baseline_forecast_usd: float
    simulated_revenue_usd: float
    variance_penalty_usd: float
    risk_class: RiskClassEnum
    root_causes: List[str]
    waterfall_bridge: Optional[WaterfallVarianceBridge] = None
    executive_briefing: str
    human_approval_status: str
    audit_trail_recorded: bool
    latency_ms: int
    guardrail_verdict: GuardrailVerdictEnum = GuardrailVerdictEnum.PERMIT


class SimulationRequest(BaseModel):
    region: RegionEnum
    baseline_revenue_usd: float = Field(gt=0.0)
    slippage_percentage: float = Field(ge=0.0, le=1.0)
    cost_inflation_percentage: float = Field(default=0.0, ge=0.0, le=1.0)


class SimulationResponse(BaseModel):
    region: RegionEnum
    baseline_revenue_usd: float
    simulated_revenue_usd: float
    variance_penalty_usd: float
    adjusted_ebitda_usd: float
    waterfall: WaterfallVarianceBridge
    tie_out_verified: bool


class AuditLogEvent(BaseModel):
    event_id: str
    execution_id: str
    timestamp: datetime
    caller_identity: str
    region: RegionEnum
    fiscal_period: str
    event_type: str
    input_prompt_fingerprint: str
    tools_called: List[str]
    model_id: str
    baseline_forecast_usd: Optional[float] = None
    simulated_revenue_usd: Optional[float] = None
    variance_penalty_usd: Optional[float] = None
    applied_risk_penalty_pct: Optional[float] = None
    latency_ms: int
    executive_briefing_hash: Optional[str] = None
    guardrail_verdict: GuardrailVerdictEnum
    audit_metadata: Dict[str, Any] = Field(default_factory=dict)
