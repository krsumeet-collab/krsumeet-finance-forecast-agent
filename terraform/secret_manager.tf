# Secret Manager for upstream CRM, Workday, and Bloomberg API credentials
resource "google_secret_manager_secret" "crm_api_credentials" {
  secret_id = "fpa-salesforce-credentials"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "workday_api_credentials" {
  secret_id = "fpa-workday-credentials"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "bloomberg_api_credentials" {
  secret_id = "fpa-bloomberg-credentials"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}
