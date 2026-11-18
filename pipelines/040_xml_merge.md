# 040 · XML: a parse step, then merge on a primary key

**Goal:** load two XML snapshots of the same orders, where some orders have changed status in between, and see dlt update those orders instead of adding them again. Then keep the full status history.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| Parse step | dlt can't read XML directly. `parse_orders()` turns each `<order>` into a dict, with its `<order_line>` elements as a list. After that it's the same path as lab 020's JSON. XML has no types, so every value is text. |
| Primary key | `primary_key="order_id"`: how dlt recognises an order it has seen before. |
| Merge | `write_disposition={"disposition": "merge", "strategy": ...}`: existing orders are updated and new ones added. The strategies are `delete-insert` (used here), `upsert` (same result here) and `scd2` (keeps history). |
| Staging dataset | dlt loads into `lab_040_xml_merge_staging` first, then merges into the real tables. |
| `_dlt_root_id` | Added to child rows when merging: the order a line belongs to, so dlt replaces an order's lines together with the order. |

## The data

Two files in `data/040_xml_merge/`. Each one is a snapshot of all orders at that time, with their lines nested inside them:

| File | Contents |
|------|----------|
| `orders_v1.xml` | 10 October: the same 8 orders and 15 lines as lab 010. |
| `orders_v2.xml` | 10 November: the 8 orders again, 5 of them with a new status, plus lab 030's 4 November orders. 12 orders and 22 lines. |

## Run

The script loads the file in `FILE`, which starts as `orders_v1.xml`:

```powershell
python pipelines/040_xml_merge.py
```

## Explore

In `db/db_explore.ipynb`:

```python
q("select * from lab_040_xml_merge.orders order by order_id")
q("select * from lab_040_xml_merge.orders__order_lines")
q("select status, count(*) as orders from lab_040_xml_merge.orders group by 1")
```

## Try this

1. **Load the later snapshot.** Set `FILE = "orders_v2.xml"` and run.
   - `orders` now has 12 rows, each order once. Orders 1003–1006 and 1008 have their new status, and 1009–1012 are new. `orders__order_lines` has 22 rows.
   - Run again: nothing changes. Compare that with `append` in lab 010, where every run added the rows again.

2. **Keep the history with `scd2`.** In the script, change `"strategy": "delete-insert"` to `"strategy": "scd2"`. Then:
   - Start over: set `FILE` back to `orders_v1.xml`, change the last lines to `pipeline.run(sales_orders(FILE), refresh="drop_sources")` and run.
   - Remove `refresh=...`, set `FILE = "orders_v2.xml"` and run again.

   `orders` now has 17 rows: every order that changed has two versions, with `_dlt_valid_from` and `_dlt_valid_to` showing when each was valid. The validity times are the load times.
   ```python
   q("select order_id, status, _dlt_valid_from, _dlt_valid_to from lab_040_xml_merge.orders order by order_id, _dlt_valid_from")
   ```
   The current state is the rows that are still valid, 12 of them:
   ```python
   q("select order_id, status from lab_040_xml_merge.orders where _dlt_valid_to is null order by order_id")
   ```

3. **Load a snapshot that is missing orders.** Still with `scd2`, set `FILE = "orders_v1.xml"` and run. Orders 1009–1012 aren't in that file, so dlt closes them: their `_dlt_valid_to` is set. `scd2` treats every load as the complete truth. Use `delete-insert` or `upsert` when a file only holds some of the rows.

   Afterwards, set the strategy back to `delete-insert` and start over with v1 as in step 2.

## Takeaways

- XML needs a parse step into dicts. From there, dlt treats it like JSON.
- A primary key plus `merge` makes reruns and new snapshots update rows instead of duplicating them.
- `scd2` keeps every version of a row, but it expects each load to be a complete snapshot.
