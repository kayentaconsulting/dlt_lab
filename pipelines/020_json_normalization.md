# 020 · JSON normalization: nested data becomes related tables

**Goal:** load the same orders and order lines as lab 010, this time from one JSON file with the lines nested inside each order, and see dlt build the two related tables for you.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| Normalization | dlt's normalize step flattens nested data into tables before loading. |
| Child table | The nested list `order_lines` becomes its own table, `orders__order_lines`: parent name, `__`, field name. |
| `_dlt_parent_id` | On every child row: the `_dlt_id` of the order it belongs to. That's the link dlt creates. |
| `_dlt_list_idx` | The line's position in its list, starting at 0. |
| Nested objects | An object (not a list) is flattened into the parent's columns: `address.city` becomes `address__city`. |

## The data

`data/020_json_normalization/orders.json` holds the same 8 orders and 15 order lines as the two CSV files in lab 010, as one list of orders:

```json
{
  "order_id": 1001,
  "order_date": "2026-10-01",
  "customer_name": "Anna Lindqvist",
  ...
  "order_lines": [
    {"line_number": 1, "product": "Kaffebryggare", "quantity": 1, "unit_price": 899.00},
    {"line_number": 2, "product": "Kaffefilter 100 st", "quantity": 2, "unit_price": 29.90}
  ]
}
```

The lines have no `order_id`: their place inside the order says which order they belong to.

## Run

```powershell
python pipelines/020_json_normalization.py
```

## Explore

In `db/db_explore.ipynb`:

```python
q("select * from lab_020_json_normalization.orders")
q("select * from lab_020_json_normalization.orders__order_lines")
```

The two tables have 8 and 15 rows, like the CSV files. To join each order to its lines, use `_dlt_parent_id` → `_dlt_id`:

```python
q("""
select o.order_id, o.customer_name, l.line_number, l.product, l.quantity, l.unit_price
from lab_020_json_normalization.orders as o
join lab_020_json_normalization.orders__order_lines as l on l._dlt_parent_id = o._dlt_id
order by o.order_id, l.line_number
""")
```

The result is the same as the join in lab 010. The difference is that dlt created the relation, instead of you joining on `order_id`.

## Try this

1. **Prove it matches lab 010.** Run lab 010 first if you haven't yet. This query returns no rows, which means every line from the JSON also exists in the CSV:
   ```python
   q("""
   select o.order_id, l.line_number, l.product, l.quantity, l.unit_price
   from lab_020_json_normalization.orders as o
   join lab_020_json_normalization.orders__order_lines as l on l._dlt_parent_id = o._dlt_id
   except
   select order_id::bigint, line_number::bigint, product, quantity::bigint, unit_price::double
   from lab_010_csv_basics.order_lines
   """)
   ```
2. **Nest an object.** In `orders.json`, replace `"city": "Stockholm", "country": "SE"` in order 1001 with `"address": {"city": "Stockholm", "country": "SE"}` and run again. `orders` gets two new columns, `address__city` and `address__country`, which are filled only for order 1001. Undo the change and run again: the columns stay, now empty. dlt adds columns but never drops them.
3. **Compare the types with lab 010:**
   ```python
   q("select table_name, column_name, data_type from information_schema.columns where table_schema = 'lab_020_json_normalization'")
   ```
   JSON has numbers, so `order_id` and `quantity` are `BIGINT` and `unit_price` is `DOUBLE`, and `quantity * unit_price` now works without casts. `order_date` is still `VARCHAR`, because JSON has no date type. Lab 030 covers types.

## Takeaways

- dlt turns nested lists into child tables and links them with `_dlt_parent_id` → `_dlt_id`. You don't write any join logic.
- Nested objects become `__` columns in the parent table.
- Only the parent table has `_dlt_load_id`. Child rows are traced through their parent.
