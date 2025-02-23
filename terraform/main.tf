terraform {
  required_version = ">= 1.0"
  backend "local" {}

  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project     = var.project
  region      = var.region
}

# API
resource "google_project_service" "bigquery" {
  project = var.project
  service = "bigquery.googleapis.com"
}

resource "google_project_service" "storage" {
  project = var.project
  service = "storage.googleapis.com"
}

# Google Cloud Storage
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${local.data_lake_bucket}-${var.project}"
  location      = var.region
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30
    }
  }

  force_destroy = true
}

# BigQuery
resource "google_bigquery_dataset" "dataset" {
  dataset_id = lower(var.BQ_DATASET)
  project    = var.project
  location   = var.region
}
