"""Lab 030 · Excel: types, schema evolution and data contracts.

Loads one monthly Excel delivery of orders into DuckDB. Instructions: pipelines/030_xlsx_schema_evolution.md
"""

import dlt
from openpyxl import load_workbook

PIPELINE_NAME = "lab_030_xlsx_schema_evolution"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_030_xlsx_schema_evolution"  # the schema in the destination that holds this pipeline's tables

DATA_DIR = "data/030_xlsx_schema_evolution"  # relative to the repo root, so run from there
FILE = "orders_v1.xlsx"  # the delivery to load; change to "orders_v2.xlsx" for next month's

# COLUMN HINTS: tell dlt a column's type instead of letting it infer one from the first value.
# Excel stores every number the same way, and openpyxl returns 899.00 as an int but 29.90 as a float.
# Without the hint, the first price (899) makes unit_price a BIGINT and 29.90 ends up in a variant column.
COLUMNS = {
    "orders": {"order_date": {"data_type": "date"}},  # Excel dates arrive as datetimes; keep only the date
    "order_lines": {"unit_price": {"data_type": "double"}},
}


def read_sheet(ws):
    """Yields one dict per row. The first row holds the column names.
    Values keep the types Excel gives them: int or float for numbers, datetime for dates, str for text."""
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    for row in rows:
        if any(value is not None for value in row):  # skip empty rows
            yield dict(zip(header, row))


# SOURCE: one resource per sheet, so each sheet becomes its own table (orders, order_lines).
# "append": every delivery adds its rows to the tables.
# Schema evolution is on by default: a new column in a later delivery is added to the table, and a
# value that doesn't fit its column's type goes to a variant column, e.g. unit_price__v_text.
@dlt.source(name="sales_orders")
def sales_orders(file_name):
    workbook = load_workbook(f"{DATA_DIR}/{file_name}", read_only=True, data_only=True)
    for sheet in workbook.worksheets:
        yield dlt.resource(
            list(read_sheet(sheet)),
            name=sheet.title,
            write_disposition="append",
            columns=COLUMNS.get(sheet.title),
        )


if __name__ == "__main__":
    # PIPELINE: moves data from a source to a destination: extract -> normalize -> load.
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb("db/local_data.duckdb"),
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sales_orders(FILE))
    print(load_info)
