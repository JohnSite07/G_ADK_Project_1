
# Enable required Google Cloud APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "iam.googleapis.com",
    "storage.googleapis.com",
    "compute.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  service = each.key
}

# --- Database (Cloud SQL for PostgreSQL) ---
resource "google_sql_database_instance" "postgres" {
  name             = "wilder-db-instance"
  database_version = "POSTGRES_14"
  region           = var.gcp_region

  settings {
    tier = "db-g-1-small" # Generic, 1 vCPU, 1.7GB RAM - suitable for small projects
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "On"
    }
  }

  deletion_protection = false # Set to true for production
  depends_on = [google_project_service.apis]
}

resource "google_sql_database" "default" {
  instance = google_sql_database_instance.postgres.name
  name     = "wilderdb"
}

resource "google_sql_user" "default" {
  instance = google_sql_database_instance.postgres.name
  name     = "wilderuser"
  password = var.db_password
}

# --- Backend (Cloud Run) ---
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.gcp_region
  repository_id = "wilder-repo"
  format        = "DOCKER"
  description   = "Docker repository for the Wilder application"
  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_v2_service" "backend" {
  name     = "wilder-backend-service"
  location = var.gcp_region

  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/wilder-backend:latest"
      ports {
        container_port = 3000 # Default Next.js port
      }
      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.default.name}:${google_sql_user.default.password}@/${google_sql_database.default.name}?host=/cloudsql/${google_sql_database_instance.postgres.connection_name}"
      }
    }
  }

  depends_on = [
    google_project_service.apis,
    google_sql_database.default,
    google_sql_user.default
  ]
}

# --- Frontend (Google Cloud Storage for Static Hosting) ---
resource "google_storage_bucket" "frontend" {
  name                        = "${var.gcp_project_id}-wilder-frontend"
  location                    = "US" # GCS buckets for CDN must be multi-regional
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket_iam_member" "public_access" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
