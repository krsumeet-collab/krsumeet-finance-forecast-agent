variable "project_id" {
  description = "The Google Cloud Project ID hosting the FP&A Swarm"
  type        = string
  default     = "corp-finance-gcp"
}

variable "region" {
  description = "Primary GCP deployment region"
  type        = string
  default     = "europe-west1"
}

variable "environment" {
  description = "Deployment environment (staging/prod)"
  type        = string
  default     = "prod"
}

variable "container_image" {
  description = "Artifact Registry container image URI"
  type        = string
  default     = "europe-west1-docker.pkg.dev/corp-finance-gcp/finance-agents/forecast-agent:v1.0.0"
}

variable "cloud_run_max_instances" {
  description = "Maximum container instances for Cloud Run autoscaling"
  type        = number
  default     = 50
}

variable "cloud_run_concurrency" {
  description = "Concurrent requests per Cloud Run container"
  type        = number
  default     = 80
}
