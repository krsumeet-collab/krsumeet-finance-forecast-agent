# Dedicated VPC for FP&A Secure Multi-Agent Environment
resource "google_compute_network" "fpa_vpc" {
  name                    = "fpa-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "fpa_subnet" {
  name                     = "fpa-subnet-${var.region}"
  ip_cidr_range            = "10.10.0.0/20"
  region                   = var.region
  network                  = google_compute_network.fpa_vpc.id
  private_ip_google_access = true
}

# Serverless VPC Access Connector for Cloud Run to access private BigQuery / Redis
resource "google_vpc_access_connector" "fpa_connector" {
  name          = "fpa-vpc-conn"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.fpa_vpc.name
  min_instances = 2
  max_instances = 10
}
