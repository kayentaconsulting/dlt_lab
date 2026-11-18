"""Lab 050 · Incremental loading and state: only new files are loaded.

Reads daily order files from a folder with dlt's filesystem source, and remembers which files it has
already loaded. Instructions: pipelines/050_incremental_state.md
"""

import csv

import dlt
from dlt.sources.filesystem import filesystem

PIPELINE_NAME = "lab_050_incremental_state"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_050_incremental_state"  # the schema in the destination that holds this pipeline's tables

INCOMING = "data/050_incremental_state/incoming"  # the folder to read; relative to the repo root


# TRANSFORMER: a resource that takes its input from another resource. Here it gets the files that
# the filesystem source found, reads each one and yields its rows, with the file's name on every row.
@dlt.transformer(name="orders")
def read_orders(files):
    for file in files:
        with file.open(mode="r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                yield {**row, "file_name": file["file_name"]}


# SOURCE: the filesystem source lists the files in a folder. The same code reads from a bucket
# such as s3://, az:// or gs:// when bucket_url points there (lab 060 reads from MinIO).
@dlt.source(name="sales_orders")
def sales_orders():
    files = filesystem(
        bucket_url=INCOMING,
        file_glob="*.csv",
        # INCREMENTAL: dlt remembers the highest file name it has loaded, in the pipeline state.
        # The next run only passes on files whose name sorts after it. The names hold the date.
        incremental=dlt.sources.incremental("file_name"),
    )
    return files | read_orders  # the pipe operator feeds the files into the transformer


if __name__ == "__main__":
    # PIPELINE: moves data from a source to a destination: extract -> normalize -> load.
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb("db/local_data.duckdb"),
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sales_orders())
    print(load_info)
