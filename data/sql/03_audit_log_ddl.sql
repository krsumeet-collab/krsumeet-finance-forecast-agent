-- ============================================================================
-- BigQuery DDL: Immutable Financial Forecast Audit & Compliance Ledger
-- Project: Autonomous Finance Agent — Forecast Generation Swarm
-- ============================================================================

CREATE OR REPLACE TABLE `finance_analytics.forecast_audit_ledger` (
  event_id STRING NOT NULL OPTIONS(description="Unique UUID for audit entry"),
  execution_id STRING NOT NULL OPTIONS(description="Parent forecast execution trace ID"),
  timestamp TIMESTAMP NOT NULL OPTIONS(description="UTC timestamp of the transaction"),
  caller_identity STRING NOT NULL OPTIONS(description="Authenticated user LDAP or service account"),
  region STRING NOT NULL OPTIONS(description="Target geographic territory"),
  fiscal_period STRING NOT NULL OPTIONS(description="Forecast quarter e.g. Q3_2026"),
  event_type STRING NOT NULL OPTIONS(description="TRIGGER, RCA_COMPLETED, HITL_APPROVED, SIMULATION_RUN, BRIEFING_DISPATCHED"),
  input_prompt_fingerprint STRING NOT NULL OPTIONS(description="SHA-256 fingerprint of sanitized prompt"),
  tools_called ARRAY<STRING> OPTIONS(description="List of tools invoked in this lifecycle step"),
  model_id STRING NOT NULL OPTIONS(description="Gemini / TimesFM model identifier used"),
  baseline_forecast_usd NUMERIC(15, 2) OPTIONS(description="Pre-simulation baseline revenue"),
  simulated_revenue_usd NUMERIC(15, 2) OPTIONS(description="Simulated risk-adjusted revenue"),
  variance_penalty_usd NUMERIC(15, 2) OPTIONS(description="Calculated variance miss"),
  applied_risk_penalty_pct FLOAT64 OPTIONS(description="Risk percentage haircut applied"),
  latency_ms INT64 NOT NULL OPTIONS(description="Execution latency in milliseconds"),
  executive_briefing_hash STRING OPTIONS(description="SHA-256 hash of generated narrative text"),
  guardrail_verdict STRING NOT NULL OPTIONS(description="PERMIT, SANITIZE, or BLOCK"),
  audit_metadata JSON OPTIONS(description="Structured JSON containing full RCA findings and approvals")
)
PARTITION BY DATE(timestamp)
CLUSTER BY region, caller_identity, event_type;
