# 010 · CSV basics: the core dlt objects

**Goal:** load two related CSV files, orders and their order lines, into DuckDB, and meet the objects every dlt pipeline is built from.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| Resource | `orders()` and `order_lines()`: functions that yield rows. Each resource becomes a table. |
| Source | `sales_orders()`: groups the two resources. They load in the same run, so both tables get the same load id. |
| Pipeline | `dlt.pipeline(...)`: runs extract → normalize → load and remembers its state. |
| Destination | `dlt.destinations.duckdb(...)`: where the data lands. |
| Dataset | `lab_010_csv_basics`: the schema in DuckDB that holds the tables. |
| Write disposition | `append` adds the rows on every run. `replace` swaps each table for the new rows. |

## The data

Both files are in `data/010_csv_basics/`, comma-separated and UTF-8. Open them.

| File | Rows | One row is |
|------|------|------------|
| `orders.csv` | 8 | an order: date, customer, city, status |
| `order_lines.csv` | 15 | one product on an order: quantity and unit price |

`order_id` in `order_lines.csv` points to an order in `orders.csv`. dlt doesn't know about this relation: you join on it yourself. Lab 020 shows dlt creating the relation for you from nested JSON.

## Run

```powershell
python pipelines/010_csv_basics.py
```

## Explore

In `db/db_explore.ipynb`:

```python
q("select * from lab_010_csv_basics.orders")
q("select * from lab_010_csv_basics.order_lines")
q("select * from lab_010_csv_basics._dlt_loads")
```

To join each order to its lines:

```python
q("""
select o.order_id, o.customer_name, l.line_number, l.product, l.quantity, l.unit_price
from lab_010_csv_basics.orders as o
join lab_010_csv_basics.order_lines as l on l.order_id = o.order_id
order by o.order_id, l.line_number
""")
```

- Both tables have two dlt columns:
  - `_dlt_load_id` says which load a row came from. It's the same in both tables, because they loaded together.
  - `_dlt_id` is a unique row id.
- `_dlt_loads` has one row per load. `status` 0 means it succeeded.

## Try this

1. **Run it again.** Now `orders` has 16 rows and `order_lines` 30, because `append` added both files once more. The join returns 60 rows instead of 15, since every line matches both copies of its order. Count the rows per load:
   ```python
   q("select _dlt_load_id, count(*) as rows from lab_010_csv_basics.orders group by 1")
   ```
2. **Follow a run through `~/.dlt`.** dlt does its work in the pipeline's working folder, `~/.dlt/pipelines/lab_010_csv_basics/` (on Windows `C:\Users\<you>\.dlt\pipelines\lab_010_csv_basics\`). After a run, `normalize/extracted/` and `load/normalized/` are empty: each folder is cleared once the next step has taken over the package. To see them filled, change the last lines of the script so the steps run one at a time:
   ```python
   pipeline.extract(sales_orders())
   input("Extracted: look in normalize/extracted/, then press Enter")
   pipeline.normalize()
   input("Normalized: extracted/ is empty again, look in load/normalized/, then press Enter")
   print(pipeline.load())
   ```
   Run it and look in the folders at each pause. There's one gzip-compressed file per table: `orders.<id>.typed-jsonl.gz` after extract, `orders.<id>.insert_values.gz` after normalize. After the load, the package is in `load/loaded/<load_id>/`, with the load files in `completed_jobs/`. This run appended the data a third time; the next exercise sets that straight.
3. **Switch to `replace`.** Change the last lines of the script to `pipeline.run(sales_orders(), write_disposition="replace")` and run. A setting on `run()` overrides the one on each resource, so both tables are back to 8 and 15 rows. `_dlt_loads` still lists every load.
4. **Check the types:**
   ```python
   q("select table_name, column_name, data_type from information_schema.columns where table_schema = 'lab_010_csv_basics' and table_name in ('orders', 'order_lines')")
   ```
   Every column is `VARCHAR`, even `quantity` and `unit_price`. The CSV reader hands dlt strings, so dlt stores strings. That's why this query fails:
   ```python
   q("select sum(quantity * unit_price) from lab_010_csv_basics.order_lines")
   ```
   Until you cast: `sum(quantity::int * unit_price::double)`. Lab 030 covers types.

## Takeaways

- A resource is just a Python generator. dlt creates the table and its columns for you.
- A source groups related resources, which load together under one load id.
- The write disposition decides whether a rerun adds rows (`append`) or overwrites the table (`replace`).
- Every row can be traced to its load through `_dlt_load_id` and `_dlt_loads`.
