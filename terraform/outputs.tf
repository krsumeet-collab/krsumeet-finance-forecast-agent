output "cloud_run_service_url" {
  description = "The deployed Cloud Run Gateway URL"
  value       = google_cloud_run_v2_service.forecast_agent_service.uri
}

output "service_account_email" {
  description = "Service account assigned to the Forecast Swarm"
  value       = google_service_account.fpa_agent_sa.email
}

output "bigquery_dataset_id" {
  description = "BigQuery analytics dataset ID"
  value       = google_bigquery_dataset.finance_analytics.dataset_id
}

output "vpc_connector_id" {
  description = "Serverless VPC access connector ID"
  value       = google_vpc_access_connector.fpa_connector.id
}
