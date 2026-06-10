# Enable required Google Cloud services
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry_api" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build_api" {
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Create an Artifact Registry repository to store the Docker image
resource "google_artifact_registry_repository" "repo" {
  provider      = google
  location      = var.region
  repository_id = var.repo_name
  description   = "Docker repository for the application image"
  format        = "DOCKER"
  depends_on = [
    google_project_service.artifact_registry_api
  ]
}

# Define the image URL locally. The deploy script ensures the image exists before this is needed.
locals {
  image_url = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/${var.app_name}:latest"
}

# Create the Cloud Run service
resource "google_cloud_run_v2_service" "service" {
  provider = google
  name     = var.app_name
  location = var.region

  template {
    containers {
      image = local.image_url
      ports {
        container_port = 3000
      }
    }
  }

  depends_on = [
    google_project_service.run_api
  ]
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  provider = google
  location = google_cloud_run_v2_service.service.location
  service  = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
