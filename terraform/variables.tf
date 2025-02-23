locals {
  data_lake_bucket = "spotify"
}

variable "project" {
  description = "GCP Project ID"
  type        = string
  default     = "data-engineering-spotify"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west6"
}

variable "storage_class" {
  description = "GCS Storage Class"
  type        = string
  default     = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Data Set"
  type        = string
  default     = "spotify"
}
