
variable "gcp_project_id" {
  description = "The Google Cloud project ID to deploy to."
  type        = string
}

variable "gcp_region" {
  description = "The Google Cloud region to deploy resources in."
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "The password for the PostgreSQL database user."
  type        = string
  sensitive   = true
}

variable "repo_name" {
  description = "The name of the GitHub repository (e.g., 'owner/repo')."
  type        = string
}
