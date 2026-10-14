-- ============================================================================
-- BigQuery DDL: CRM Opportunity Pipeline & BigQuery ML ARIMA-Plus Time-Series
-- Project: Autonomous Finance Agent — Forecast Generation Swarm
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS `finance_analytics`
OPTIONS (
  location = 'europe-west1',
  description = 'Corporate FP&A Analytics, Pipeline, and Time-Series Forecasting Dataset'
);

-- Table: CRM Ingested Opportunities
CREATE OR REPLACE TABLE `finance_analytics.crm_pipeline_opportunities` (
  opportunity_id STRING NOT NULL OPTIONS(description="Salesforce 18-character Opportunity ID"),
  account_id STRING NOT NULL OPTIONS(description="Anonymized Customer Account ID"),
  deal_name STRING NOT NULL OPTIONS(description="DLP-sanitized opportunity title"),
  region STRING NOT NULL OPTIONS(description="Operating territory: EMEA, LATAM, NA, APAC"),
  territory_id STRING NOT NULL OPTIONS(description="Sales sub-territory code"),
  stage_name STRING NOT NULL OPTIONS(description="Salesforce stage name"),
  probability FLOAT64 NOT NULL OPTIONS(description="Probability of closure (0.00 to 1.00)"),
  amount_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Contract amount in USD"),
  weighted_amount_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Expected value: amount_usd * probability"),
  expected_close_date DATE NOT NULL OPTIONS(description="Projected contract close date"),
  is_stalled BOOL NOT NULL OPTIONS(description="True if deal has had no stage change in >21 days"),
  last_activity_date TIMESTAMP NOT NULL OPTIONS(description="Timestamp of last CRM note or customer call"),
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY expected_close_date
CLUSTER BY region, territory_id;

-- BigQuery ML Model: ARIMA-Plus Time Series Model for Revenue Forecasting
CREATE OR REPLACE MODEL `finance_analytics.arima_plus_revenue_model`
OPTIONS (
  model_type = 'ARIMA_PLUS',
  time_series_timestamp_col = 'period_end_date',
  time_series_data_col = 'recognized_revenue_usd',
  time_series_id_col = 'region',
  holiday_region = 'GLOBAL',
  auto_arima = TRUE,
  data_frequency = 'MONTHLY'
) AS
SELECT
  PARSE_DATE('%Y-%m', fiscal_period) AS period_end_date,
  region,
  recognized_revenue_usd
FROM
  `finance_analytics.erp_general_ledger_actuals`
WHERE
  recognized_revenue_usd IS NOT NULL;
