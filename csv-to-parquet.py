import pandas as pd
from google.cloud import storage


def convert_csv_to_parquet(csv_file_path: str, parquet_file_path: str) -> None:
    """
    Reads a CSV file into a DataFrame and writes it as a Parquet file.
    """
    df = pd.read_csv(csv_file_path)
    df.to_parquet(parquet_file_path, engine='pyarrow', index=False)
    print(f"Converted {csv_file_path} to {parquet_file_path}")


def upload_to_gcs(bucket_name: str, source_file_path: str, destination_blob_name: str, project_id: str) -> None:
    """
    Uploads a local file to a GCS bucket within the specified GCP project.
    """
    # Create a storage client for the specified project
    client = storage.Client(project=project_id)

    # Retrieve the bucket
    bucket = client.bucket(bucket_name)

    # Create a blob object from the file path
    blob = bucket.blob(destination_blob_name)

    # Upload the file to GCS
    blob.upload_from_filename(source_file_path)
    print(f"Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")


if __name__ == "__main__":
    # Local paths
    csv_file = "cleaned_tracks_features.csv"
    parquet_file = "cleaned_tracks_features.parquet"

    # GCP details
    bucket_name = "spotify-data-engineering-spotify"
    project_id = "data-engineering-spotify"

    # Convert CSV to Parquet
    convert_csv_to_parquet(csv_file, parquet_file)

    # Upload Parquet to GCS
    upload_to_gcs(
        bucket_name=bucket_name,
        source_file_path=parquet_file,
        destination_blob_name="cleaned_tracks_features.parquet",
        project_id=project_id
    )
