# Autonomous Finance Agent — Forecast Generation Swarm

**Author:** Sumeet Kumar (Googler LDAP: `krsumeet`)  


---

## 1. Project Overview

The **Autonomous Forecast Generation Swarm** is a production-grade multi-agent financial planning system built on Google Cloud Platform. It autonomously detects quarterly revenue misses, conducts parallel internal and external Root Cause Analysis (RCA), pauses execution at an interactive Human-in-the-Loop (HITL) governance gate, triggers zero-shot foundation model forecasting (Vertex AI TimesFM / BigQuery ML ARIMA-Plus), and synthesizes audit-grounded executive briefings in **under 30 seconds**.

### Key Business & Technical Outcomes
* **Cycle Latency:** Reduced enterprise quarterly forecast cycle from **3–4 weeks to < 30 seconds (P95)**.
* **Driver Attribution Precision:** **100.0% accuracy** on the 52-scenario Golden Benchmark (DoD Target: ≥ 95.0%).
* **Numerical Fidelity:** **100% exact tie-out** between narrative figures and underlying mathematical engines.
* **AI Cost Efficiency:** Model tiering reduces query compute cost to **$0.14 per forecast** (Target: < $0.20).
* **Adversarial Security:** **100% interception** of prompt injections and data exfiltration attempts.

---

## 2. System Architecture

```mermaid
flowchart TD
    Client[Executive FP&A Portal / Google Chat] -->|OAuth2 / OIDC| APIGW[FastAPI Gateway / Cloud Run]
    
    subgraph Security_Perimeter["Security & Privacy Perimeter"]
        APIGW --> DLP[Cloud DLP Sanitizer]
        DLP --> Guardrails[Pre-Execution Guardrails & Scope Defense]
    end

    subgraph Agent_Core["Google ADK Multi-Agent Core"]
        Guardrails --> Master[Master Forecast Orchestrator (Root Agent)\nGemini 2.5 Pro (Thinking Budget)]
        
        Master -->|A2A Task Dispatch| PMA[Pipeline Monitoring Sub-Agent]
        Master -->|A2A Task Dispatch| SAA[Sales Activity Sub-Agent]
        Master -->|A2A Task Dispatch| MIA[Market Intelligence Sub-Agent]
        Master -->|A2A Task Dispatch| FGA[Forecast Generation Sub-Agent]
        Master -->|A2A Task Dispatch| LNA[Leadership Notification Sub-Agent]
    end

    subgraph Upstream_Data_and_Tools["Enterprise Tools & Services"]
        PMA --> LookerTool[Looker KPI & BQ Historical Baseline]
        SAA --> SFDCTool[Salesforce CRM (MCP) & Workday HR API]
        MIA --> BloombergTool[Bloomberg Enterprise Market Wires API]
        FGA --> BQMLTool[BigQuery ML ARIMA+ / Vertex TimesFM]
        FGA --> MathTool[Deterministic Financial Variance Engine]
    end

    subgraph Governance_and_Compliance["Audit & Human Oversight"]
        Master -->|Interactive Card| HITL[Human-in-the-Loop Gate (FP&A Director)]
        Master --> AuditSink[Structured Audit Logger\nCloud Logging + BigQuery Ledger]
        Master --> PubSub[Cloud Pub/Sub Event Broadcaster]
    end
```

---

## 3. Directory Structure & Complete Artifact Map

```
finance_forecast_agent/
├── docs/
│   ├── phase1_plan_and_discover/
│   │   ├── functional_requirements_document.md     # Master PRD / FRD
│   │   ├── fpa_forecasting_rules_specification.md  # Domain mathematics & variance rules
│   │   ├── data_and_deploy_discovery.md            # Ingestion streams, DLP & Cloud Run sizing
│   │   ├── grounding_and_api_discovery.md          # Tools, MCP & circuit breakers
│   │   └── financial_timeseries_schema_catalog.md  # Data dictionary
│   ├── phase2_architecture/
│   │   ├── technical_design_document_part1.md      # System topology & threat model
│   │   ├── technical_design_document_part2.md      # App scaffolding & interfaces
│   │   ├── openapi_rest_specification.yaml         # OpenAPI 3.1 REST contracts
│   │   └── adrs/
│   │       ├── ADR-001_multi_agent_swarm_vs_monolithic.md
│   │       ├── ADR-002_bigquery_ml_arima_timesfm_vs_automl.md
│   │       └── ADR-003_deterministic_monte_carlo_vs_llm_estimation.md
│   ├── phase4_manuals_and_reports/
│   │   ├── operational_runbook.md                  # Daily maintenance & incident triage
│   │   ├── developer_onboarding_guide.md           # Local setup & testing commands
│   │   ├── fpa_user_demonstration_walkthrough.md   # Step-by-step user journey guide
│   │   ├── product_readiness_review_deck.md        # PRR presentation deck
│   │   ├── cost_and_forecasting_efficiency_report.md# Token economics & ROI model
│   │   └── final_technical_business_summary_report.md # Closure report
│   └── fde_packet/
│       ├── updated_fde_packet.md                   # Complete revised FDE Promotion Packet
│       └── fde_panel_defense_cheatsheet.md         # Interview defense Q&A playbook
├── data/
│   ├── golden_dataset/
│   │   ├── golden_scenarios.json                   # 52 enterprise ground-truth scenarios
│   │   └── annotation_guidelines.md                # Annotation rules & rubric
│   └── sql/
│       ├── 01_forecast_timeseries_ddl.sql          # BigQuery CRM & ARIMA-Plus DDL
│       ├── 02_erp_actuals_ledger_ddl.sql           # ERP trailing actuals ledger DDL
│       └── 03_audit_log_ddl.sql                    # SOX compliance audit ledger DDL
├── terraform/                                      # 100% Zero-Touch IaC
│   ├── main.tf, variables.tf, outputs.tf
│   ├── networking.tf, bigquery.tf, cloud_run.tf, iam.tf, secret_manager.tf
├── ci_cd/
│   ├── cloudbuild.yaml                             # Automated CI/CD pipeline
│   └── Dockerfile                                  # Multi-stage container with uv
├── configs/
│   ├── agent_config.yaml, prompts.yaml, monitoring_dashboards.json
├── src/                                            # Core Application Source Code
│   ├── config.py
│   ├── interfaces/ (data_stream.py, forecasting_engine.py, simulation_engine.py)
│   ├── models/schemas.py                           # Pydantic v2 data models
│   ├── security/ (guardrails.py, dlp_sanitizer.py)
│   ├── tools/ (financial_math_engine.py, crm_salesforce_tool.py, workday_hr_tool.py, ...)
│   ├── agents/ (orchestrator.py, swarm_agents.py)
│   ├── observability/ (telemetry.py, pubsub_broadcaster.py)
│   └── api/app.py                                  # FastAPI application server
├── forecast_generation_agent/                      # ADK Spec Package Aliases (agent.py, fast_api_app.py)
├── tests/                                          # Unit, Integration & Chaos Test Suites
│   ├── conftest.py, test_guardrails.py, test_financial_math.py, test_tools.py, ...
├── eval/
│   ├── run_eval.py                                 # Automated benchmark quality gate
│   └── eval_baseline_report.json                   # Certified evaluation results
├── Makefile, pyproject.toml, README.md, DEMO_RECORDING_SCRIPT.md
```

---

## 4. How to Run, Test, and Verify Everything Step-by-Step

### Step 1: Activate Virtual Environment

### Step 2: Run the Automated Evaluation Benchmark (52 Scenarios)

### Step 3: Run the Full Test Suite with Code Coverage Enforcement

### Step 4: Start the Local FastAPI Gateway Server

### Step 5: Test the Live Interactive Endpoints
