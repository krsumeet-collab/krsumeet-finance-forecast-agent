-- ============================================================================
-- BigQuery DDL: ERP General Ledger Trailing Monthly Actuals
-- Project: Autonomous Finance Agent — Forecast Generation Swarm
-- ============================================================================

CREATE OR REPLACE TABLE `finance_analytics.erp_general_ledger_actuals` (
  fiscal_period STRING NOT NULL OPTIONS(description="Month period string YYYY-MM"),
  fiscal_quarter STRING NOT NULL OPTIONS(description="Quarter period string Q[1-4]_YYYY"),
  region STRING NOT NULL OPTIONS(description="Operating territory"),
  recognized_revenue_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="GAAP recognized top-line revenue"),
  cost_of_goods_sold_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Direct hosting & cloud infrastructure COGS"),
  gross_profit_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Revenue minus COGS"),
  opex_rnd_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Research & Development expense"),
  opex_sga_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Sales, General & Administrative expense"),
  ebitda_usd NUMERIC(15, 2) NOT NULL OPTIONS(description="Operating EBITDA"),
  ebitda_margin_pct FLOAT64 NOT NULL OPTIONS(description="EBITDA / Revenue"),
  headcount_actuals INT64 NOT NULL OPTIONS(description="Active FTE headcount in region"),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY PARSE_DATE('%Y-%m', fiscal_period)
CLUSTER BY region;
