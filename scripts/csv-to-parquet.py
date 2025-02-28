import pandas as pd
from google.cloud import storage


def convert_csv_to_parquet(csv_file_path: str, parquet_file_path: str) -> None:
    df = pd.read_csv(csv_file_path)
    df.to_parquet(parquet_file_path, engine='pyarrow', index=False)
    print(f"Converted {csv_file_path} to {parquet_file_path}")


def upload_to_gcs(
        bucket_name: str,
        source_file_path: str,
        destination_blob_name: str,
        project_id: str,
        chunk_size_mb: int = 5,
        timeout: int = 300
) -> None:
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Set a custom chunk size (in bytes); must be a multiple of 256 KB.
    blob.chunk_size = chunk_size_mb * 1024 * 1024

    # Upload the file using the specified timeout (in seconds).
    blob.upload_from_filename(source_file_path, timeout=timeout)

    print(f"Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")


if __name__ == "__main__":
    csv_file = "cleaned_tracks_features.csv"
    parquet_file = "cleaned_tracks_features.parquet"

    bucket_name = "spotify-data-engineering-spotify"
    project_id = "data-engineering-spotify"

    # 1) Convert CSV to Parquet
    convert_csv_to_parquet(csv_file, parquet_file)

    # 2) Upload Parquet to GCS with custom chunk size and increased timeout
    upload_to_gcs(
        bucket_name=bucket_name,
        source_file_path=parquet_file,
        destination_blob_name="cleaned_tracks_features.parquet",
        project_id=project_id,
        chunk_size_mb=5,  # smaller chunks can help avoid timeouts on slower networks
        timeout=300  # 5-minute total upload timeout
    )
