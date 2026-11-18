"""Lab 010 · CSV basics: the core dlt objects.

Loads two related CSV files, orders and their order lines, into DuckDB.
Instructions: pipelines/010_csv_basics.md
"""

import csv

import dlt

PIPELINE_NAME = "lab_010_csv_basics"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_010_csv_basics"  # DATASET: the schema in the destination that holds this pipeline's tables

DATA_DIR = "data/010_csv_basics"  # relative to the repo root, so run from there


def read_csv(file_name):
    """Yields one dict per row, e.g. {"order_id": "1001", "order_date": "2026-10-01", ...}"""
    with open(f"{DATA_DIR}/{file_name}", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


# RESOURCE: a function that yields data. dlt turns each resource into a table, here `orders`.
# write_disposition decides what happens to rows already in the table:
# "append" adds the new rows, "replace" swaps the whole table for the new rows.
@dlt.resource(name="orders", write_disposition="append")
def orders():
    yield from read_csv("orders.csv")


# A second resource and table: one row per product on an order. order_id links a line to its order.
@dlt.resource(name="order_lines", write_disposition="append")
def order_lines():
    yield from read_csv("order_lines.csv")


# SOURCE: groups resources that belong together. Orders and their lines load in the same run,
# so both tables always get the same load id.
# The name is also the name of the dlt schema: dlt's description of the tables, not the dataset.
@dlt.source(name="sales_orders")
def sales_orders():
    return orders(), order_lines()


if __name__ == "__main__":
    # PIPELINE: moves data from a source to a destination: extract -> normalize -> load.
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        # DESTINATION: where the data ends up. Every lab loads into the same DuckDB file.
        destination=dlt.destinations.duckdb("db/local_data.duckdb"),
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sales_orders())
    print(load_info)
