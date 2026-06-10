# Enable required Google Cloud services
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry_api" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild_api" {
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Create an Artifact Registry repository to store the Docker image
resource "google_artifact_registry_repository" "repository" {
  location      = var.gcp_region
  repository_id = var.repository_id
  format        = "DOCKER"
  project       = var.gcp_project_id

  depends_on = [google_project_service.artifactregistry_api]
}

# Create the Cloud Run service
resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.gcp_region
  project  = var.gcp_project_id

  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repository.repository_id}/${var.service_name}:latest"
      ports {
        container_port = 3000
      }
    }
  }

  depends_on = [google_project_service.run_api, google_artifact_registry_repository.repository]
}

# Allow unauthenticated access to the service
resource "google_cloud_run_v2_service_iam_binding" "no_auth" {
  project  = google_cloud_run_v2_service.service.project
  location = google_cloud_run_v2_service.service.location
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  members = [
    "allUsers",
  ]
}

# A note about static assets:
# For a real-world high-performance setup, the static assets (.js, .css, images)
# from the Next.js build output (`.next/static`) would be uploaded to a
# Google Cloud Storage bucket and served through a Google Cloud CDN.
# This would offload traffic from the Cloud Run instance.
# For this exercise, we'll keep it simple and let the Cloud Run instance
# serve all assets, which is a valid and simpler deployment pattern.
