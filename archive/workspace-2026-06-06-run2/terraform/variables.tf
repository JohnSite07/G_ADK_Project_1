variable "gcp_project_id" {
  description = "The Google Cloud project ID to deploy the resources to."
  type        = string
}

variable "gcp_region" {
  description = "The Google Cloud region to deploy the resources to."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "story-of-everything"
}

variable "repository_id" {
  description = "The ID of the Artifact Registry repository."
  type        = string
  default     = "story-of-everything-repo"
}
