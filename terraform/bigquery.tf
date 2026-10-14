# BigQuery Analytics Dataset
resource "google_bigquery_dataset" "finance_analytics" {
  dataset_id                  = "finance_analytics"
  friendly_name               = "Corporate Finance Analytics"
  description                 = "Time-series forecasting, CRM opportunities, and audit ledger"
  location                    = var.region
  default_table_expiration_ms = null

  labels = {
    env        = var.environment
    workload   = "fpa-swarm"
    compliance = "sox"
  }
}

# BigQuery Table: Pipeline Opportunities
resource "google_bigquery_table" "crm_opportunities" {
  dataset_id          = google_bigquery_dataset.finance_analytics.dataset_id
  table_id            = "crm_pipeline_opportunities"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "expected_close_date"
  }

  clustering = ["region", "territory_id"]

  schema = jsonencode([
    {"name": "opportunity_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "account_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "deal_name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "region", "type": "STRING", "mode": "REQUIRED"},
    {"name": "territory_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "stage_name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "probability", "type": "FLOAT", "mode": "REQUIRED"},
    {"name": "amount_usd", "type": "NUMERIC", "mode": "REQUIRED"},
    {"name": "weighted_amount_usd", "type": "NUMERIC", "mode": "REQUIRED"},
    {"name": "expected_close_date", "type": "DATE", "mode": "REQUIRED"},
    {"name": "is_stalled", "type": "BOOL", "mode": "REQUIRED"},
    {"name": "last_activity_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "ingested_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
  ])
}

# BigQuery Table: Audit Ledger
resource "google_bigquery_table" "audit_ledger" {
  dataset_id          = google_bigquery_dataset.finance_analytics.dataset_id
  table_id            = "forecast_audit_ledger"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["region", "caller_identity", "event_type"]

  schema = jsonencode([
    {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "execution_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "caller_identity", "type": "STRING", "mode": "REQUIRED"},
    {"name": "region", "type": "STRING", "mode": "REQUIRED"},
    {"name": "fiscal_period", "type": "STRING", "mode": "REQUIRED"},
    {"name": "event_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "input_prompt_fingerprint", "type": "STRING", "mode": "REQUIRED"},
    {"name": "tools_called", "type": "STRING", "mode": "REPEATED"},
    {"name": "model_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "baseline_forecast_usd", "type": "NUMERIC", "mode": "NULLABLE"},
    {"name": "simulated_revenue_usd", "type": "NUMERIC", "mode": "NULLABLE"},
    {"name": "variance_penalty_usd", "type": "NUMERIC", "mode": "NULLABLE"},
    {"name": "applied_risk_penalty_pct", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "latency_ms", "type": "INTEGER", "mode": "REQUIRED"},
    {"name": "executive_briefing_hash", "type": "STRING", "mode": "NULLABLE"},
    {"name": "guardrail_verdict", "type": "STRING", "mode": "REQUIRED"},
    {"name": "audit_metadata", "type": "JSON", "mode": "NULLABLE"}
  ])
}
