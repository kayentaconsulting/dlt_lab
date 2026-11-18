"""Lab 080 · Template: files from MinIO (S3) into SQL Server.

Reads CSV files from a MinIO bucket and loads them into SQL Server. Fill in .dlt/secrets.toml first
(copy .dlt/secrets.toml.example). Instructions: pipelines/080_minio_sqlserver.md
"""

import csv
import re

import dlt
from dlt.sources.filesystem import filesystem

PIPELINE_NAME = "lab_080_minio_sqlserver"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_080_minio_sqlserver"  # the schema in SQL Server that dlt creates; at work you'd pick your own, e.g. "src"

# Every setting this lab needs from .dlt/secrets.toml. There are no connection details in the code.
REQUIRED_SECRETS = [
    "sources.filesystem.bucket_url",
    "sources.filesystem.credentials.aws_access_key_id",
    "sources.filesystem.credentials.aws_secret_access_key",
    "sources.filesystem.credentials.endpoint_url",
    "destination.mssql.credentials.host",
    "destination.mssql.credentials.database",
    "destination.mssql.credentials.username",
    "destination.mssql.credentials.password",
]


PLACEHOLDER = re.compile(r"<[a-z-]+>")  # the placeholders in secrets.toml.example, e.g. <bucket>


def check_secrets():
    """Stops with a list of the settings that are missing, or still hold a <placeholder>."""
    missing = [
        key for key in REQUIRED_SECRETS
        if dlt.secrets.get(key, str) is None or PLACEHOLDER.search(str(dlt.secrets.get(key, str)))
    ]
    if missing:
        raise SystemExit(
            "Fill in .dlt/secrets.toml first (copy .dlt/secrets.toml.example). Missing:\n  "
            + "\n  ".join(missing)
        )


# TRANSFORMER: the same as in lab 050. Reads each file the filesystem source found, row by row.
@dlt.transformer(name="orders")
def read_orders(files):
    for file in files:
        with file.open(mode="r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                yield {**row, "file_name": file["file_name"]}


# SOURCE: the filesystem source, now reading a bucket. bucket_url and the MinIO credentials come
# from [sources.filesystem] in .dlt/secrets.toml.
@dlt.source(name="sales_orders")
def sales_orders():
    files = filesystem(
        file_glob="*.csv",
        # INCREMENTAL: in a bucket, modification_date is the upload time, so a file counts as new
        # when it was uploaded after the last run. (Lab 050 used the file names instead.)
        incremental=dlt.sources.incremental("modification_date"),
    )
    return files | read_orders


if __name__ == "__main__":
    check_secrets()

    # PIPELINE: the SQL Server credentials come from [destination.mssql.credentials].
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination="mssql",
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sales_orders())
    print(load_info)
