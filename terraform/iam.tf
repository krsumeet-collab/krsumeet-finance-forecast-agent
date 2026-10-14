# Dedicated Service Account for the Finance Agent Swarm
resource "google_service_account" "fpa_agent_sa" {
  account_id   = "sa-fpa-forecast-swarm"
  display_name = "FP&A Autonomous Forecast Swarm Service Account"
  description  = "Least-privilege execution identity for the Forecast Generation Swarm"
}

# Least-Privilege IAM Bindings
locals {
  agent_roles = [
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/secretmanager.secretAccessor",
    "roles/dlp.user",
    "roles/pubsub.publisher",
    "roles/monitoring.metricWriter"
  ]
}

resource "google_project_iam_member" "agent_role_bindings" {
  for_each = toset(locals.agent_roles)
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.fpa_agent_sa.email}"
}
