
output "cloud_run_service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_bucket_name" {
  description = "The name of the GCS bucket for the frontend assets."
  value       = google_storage_bucket.frontend.name
}

output "db_instance_connection_name" {
  description = "The connection name of the Cloud SQL database instance."
  value       = google_sql_database_instance.postgres.connection_name
}

output "artifact_registry_repository" {
  description = "The URI of the artifact registry repository."
  value = google_artifact_registry_repository.docker_repo.location
}
