output "service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.service.uri
}

output "app_name" {
    description = "The name of the application provided as a convenience output."
    value       = var.app_name
}

output "repo_name" {
    description = "The name of the Artifact Registry repository provided as a convenience output."
    value       = var.repo_name
}
