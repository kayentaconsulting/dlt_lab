"""Lab 040 · XML: a parse step, then merge on a primary key.

Loads a snapshot of all orders from XML into DuckDB, updating orders that already exist instead of
adding them again. Instructions: pipelines/040_xml_merge.md
"""

import xml.etree.ElementTree as ET

import dlt

PIPELINE_NAME = "lab_040_xml_merge"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_040_xml_merge"  # the schema in the destination that holds this pipeline's tables

DATA_DIR = "data/040_xml_merge"  # relative to the repo root, so run from there
FILE = "orders_v1.xml"  # the snapshot to load; change to "orders_v2.xml" for the later one


def parse_orders(path):
    """PARSE STEP: dlt can't read XML directly, so turn each <order> element into a Python dict.
    Child elements become keys, and the <order_line> elements become a list, like in lab 020's JSON.
    XML has no types, so every value is text."""
    root = ET.parse(path).getroot()
    for order in root.findall("order"):
        record: dict = {field.tag: field.text for field in order if field.tag != "order_lines"}
        record["order_lines"] = [
            {field.tag: field.text for field in line} for line in order.findall("order_lines/order_line")
        ]
        yield record


# RESOURCE with a merge: rows are matched on the primary key, order_id.
# "delete-insert": an order that already exists is replaced (with its lines), a new order is added.
# A rerun therefore never duplicates an order, unlike "append" in lab 010.
@dlt.resource(
    name="orders",
    primary_key="order_id",
    write_disposition={"disposition": "merge", "strategy": "delete-insert"},
)
def orders(file_name):
    yield from parse_orders(f"{DATA_DIR}/{file_name}")


# SOURCE: groups the resources. One resource, two tables (orders, orders__order_lines).
@dlt.source(name="sales_orders")
def sales_orders(file_name):
    return orders(file_name)


if __name__ == "__main__":
    # PIPELINE: moves data from a source to a destination: extract -> normalize -> load.
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb("db/local_data.duckdb"),
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sales_orders(FILE))
    print(load_info)
