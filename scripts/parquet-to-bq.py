from google.cloud import bigquery


def load_parquet_from_gcs_to_bq(
        project_id: str,
        dataset_id: str,
        table_id: str,
        gcs_uri: str
) -> None:
    """
    Loads a Parquet file from GCS into a BigQuery table.

    :param project_id: GCP project ID where the table resides (e.g., 'data-engineering-spotify')
    :param dataset_id: BigQuery dataset name (e.g., 'spotify')
    :param table_id:   Name of the target table in BigQuery (e.g., 'cleaned_tracks_features')
    :param gcs_uri:    GCS URI of the Parquet file to load (e.g., 'gs://spotify-data-engineering-spotify/cleaned_tracks_features.parquet')
    """
    client = bigquery.Client(project=project_id)

    # Full table ID in standard SQL format: project.dataset.table
    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        autodetect=True,  # Let BigQuery autodetect schema; or set your own schema if needed
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        # WRITE_TRUNCATE will overwrite the table; use WRITE_APPEND to add to it
    )

    load_job = client.load_table_from_uri(
        gcs_uri,
        full_table_id,
        job_config=job_config
    )

    print(f"Starting job to load data from {gcs_uri} into {full_table_id}...")
    load_job.result()  # Wait for job to finish

    table = client.get_table(full_table_id)
    print(f"Loaded {table.num_rows} rows into {full_table_id}.")


if __name__ == "__main__":
    # GCP / BigQuery details
    PROJECT_ID = "data-engineering-spotify"
    DATASET_ID = "spotify"
    TABLE_ID = "cleaned_tracks_features"

    # GCS info
    BUCKET_NAME = "spotify-data-engineering-spotify"
    PARQUET_FILE = "cleaned_tracks_features.parquet"
    GCS_URI = f"gs://{BUCKET_NAME}/{PARQUET_FILE}"

    # Make sure you've set your Google Application Credentials
    # e.g., export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"

    load_parquet_from_gcs_to_bq(
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        table_id=TABLE_ID,
        gcs_uri=GCS_URI
    )
