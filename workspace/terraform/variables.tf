variable "project_id" {
  type        = string
  description = "The Google Cloud project ID."
}

variable "region" {
  type        = string
  description = "The Google Cloud region to deploy resources in."
}

variable "app_name" {
  type        = string
  description = "The name of the application."
  default     = "interactive-universe"
}

variable "repo_name" {
  type        = string
  description = "The name of the Artifact Registry repository."
  default     = "app-images"
}
