"""Lab 020 · JSON normalization: nested data becomes related tables.

Loads data/020_json_normalization/orders.json: the same orders and order lines as lab 010, but in
one JSON file with each order's lines nested inside it. Instructions: pipelines/020_json_normalization.md
"""

import json

import dlt

PIPELINE_NAME = "lab_020_json_normalization"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_020_json_normalization"  # the schema in the destination that holds this pipeline's tables

DATA_FILE = "data/020_json_normalization/orders.json"  # relative to the repo root, so run from there


# RESOURCE: one resource for the whole file. Each order arrives with its lines nested inside it.
# In the normalize step dlt unpacks the nested list `order_lines` into its own child table,
# orders__order_lines, and links every line to its order with _dlt_parent_id -> _dlt_id.
# "replace", so a rerun doesn't duplicate rows (see lab 010).
@dlt.resource(name="orders", write_disposition="replace")
def orders():
    with open(DATA_FILE, encoding="utf-8") as f:
        yield from json.load(f)  # the file is a list of orders: yield them one by one


# SOURCE: groups the resources. Here just one, which still produces two tables.
@dlt.source(name="sales_orders")
def sales_orders():
    return orders()


if __name__ == "__main__":
    # PIPELINE: moves data from a source to a destination: extract -> normalize -> load.
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb("db/local_data.duckdb"),
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sales_orders())
    print(load_info)
