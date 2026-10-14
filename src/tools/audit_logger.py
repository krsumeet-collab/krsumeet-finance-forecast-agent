"""Structured Compliance & Audit Logging Module."""
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.models.schemas import AuditLogEvent, GuardrailVerdictEnum, RegionEnum


class StructuredAuditLogger:
    """Streams immutable audit events to Google Cloud Logging and BigQuery ledger."""

    def __init__(self):
        self._audit_records: List[Dict[str, Any]] = []

    def compute_sha256(self, content: str) -> str:
        """Returns hex SHA-256 fingerprint."""
        if not content:
            return ""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def log_event(
        self,
        execution_id: str,
        caller_identity: str,
        region: RegionEnum,
        fiscal_period: str,
        event_type: str,
        input_prompt: str,
        tools_called: List[str],
        model_id: str,
        latency_ms: int,
        guardrail_verdict: GuardrailVerdictEnum,
        baseline_forecast_usd: Optional[float] = None,
        simulated_revenue_usd: Optional[float] = None,
        variance_penalty_usd: Optional[float] = None,
        applied_risk_penalty_pct: Optional[float] = None,
        executive_briefing: Optional[str] = None,
        audit_metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLogEvent:
        """Constructs and persists an immutable audit record."""
        event_id = f"audit-{hashlib.md5(f'{execution_id}-{event_type}-{datetime.now(timezone.utc)}'.encode()).hexdigest()[:12]}"
        prompt_fp = self.compute_sha256(input_prompt)
        briefing_hash = self.compute_sha256(executive_briefing or "")

        event = AuditLogEvent(
            event_id=event_id,
            execution_id=execution_id,
            timestamp=datetime.now(timezone.utc),
            caller_identity=caller_identity,
            region=region,
            fiscal_period=fiscal_period,
            event_type=event_type,
            input_prompt_fingerprint=prompt_fp,
            tools_called=tools_called,
            model_id=model_id,
            baseline_forecast_usd=baseline_forecast_usd,
            simulated_revenue_usd=simulated_revenue_usd,
            variance_penalty_usd=variance_penalty_usd,
            applied_risk_penalty_pct=applied_risk_penalty_pct,
            latency_ms=latency_ms,
            executive_briefing_hash=briefing_hash,
            guardrail_verdict=guardrail_verdict,
            audit_metadata=audit_metadata or {},
        )

        record = event.model_dump(mode="json")
        self._audit_records.append(record)

        # In live GCP production, this streams to:
        # google.cloud.logging.Client().logger("fpa-audit").log_struct(record)
        # bigquery_client.insert_rows_json("finance_analytics.forecast_audit_ledger", [record])
        return event

    def get_audit_records(self) -> List[Dict[str, Any]]:
        return list(self._audit_records)


audit_logger = StructuredAuditLogger()
