# 030 · Excel: types, schema evolution and data contracts

**Goal:** load two monthly Excel deliveries of the same orders, and see how dlt types the columns, adds a column that's new in the second delivery, and handles a value that doesn't fit, unless a data contract says otherwise.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| Type inference | dlt picks each column's type from the values: int → `bigint`, float → `double`, datetime → `timestamp`, str → `text`. |
| Column hint | `columns={...}` sets a type yourself. Here `unit_price` is `double` and `order_date` is `date` (see `COLUMNS` in the script). |
| Schema evolution | A new column in a later delivery is added to the table, and older rows get NULL. Every change is a new schema version in `_dlt_version`. |
| Variant column | A value that doesn't fit its column's type goes to `<column>__v_<type>`, e.g. `unit_price__v_text`, instead of failing the load. |
| Data contract | `schema_contract` decides what may change, for tables, columns and data types: `evolve` (the default), `freeze`, `discard_row` or `discard_value`. |

## The data

Two files in `data/030_xlsx_schema_evolution/`, each with two sheets: `orders` and `order_lines`. Each sheet becomes a table.

| File | Contents |
|------|----------|
| `orders_v1.xlsx` | October: the same 8 orders and 15 lines as labs 010 and 020, with real Excel numbers and dates. |
| `orders_v2.xlsx` | November: 4 new orders and 7 lines. `orders` has a new column, `payment_method`. One line has the text `pris saknas` instead of a `unit_price`. |

## Run

The script loads the file in `FILE`, which starts as `orders_v1.xlsx`:

```powershell
python pipelines/030_xlsx_schema_evolution.py
```

## Explore

In `db/db_explore.ipynb`:

```python
q("select * from lab_030_xlsx_schema_evolution.orders")
q("select * from lab_030_xlsx_schema_evolution.order_lines")
```

Compare the types of the same columns across labs 010, 020 and 030 (run those labs first):

```python
q("""
select column_name, table_schema, data_type
from information_schema.columns
where table_schema in ('lab_010_csv_basics', 'lab_020_json_normalization', 'lab_030_xlsx_schema_evolution')
  and column_name in ('order_date', 'unit_price')
order by column_name, table_schema
""")
```

CSV gives text only. JSON has numbers but no dates. Excel has both, and the hints make sure dlt uses them as intended.

## Try this

1. **Load next month's delivery.** Set `FILE = "orders_v2.xlsx"` and run.
   - `orders` gets the column `payment_method`. It's NULL for the October orders.
   - `order_lines` gets `unit_price__v_text`, holding `pris saknas`, while `unit_price` is NULL on that row.
   - `_dlt_version` has a new row for the new schema version:
     ```python
     q("select version, inserted_at from lab_030_xlsx_schema_evolution._dlt_version")
     ```
   - In the terminal, `dlt pipeline lab_030_xlsx_schema_evolution schema` shows the new columns, and marks the variant column `variant: true`.

2. **Turn on a data contract.** First start the lab over:
   - Set `FILE` back to `orders_v1.xlsx`.
   - Change the last lines to `pipeline.run(sales_orders(FILE), refresh="drop_sources")` and run. dlt drops this lab's tables and schema, then loads October fresh.

   Then set `FILE = "orders_v2.xlsx"` and replace `refresh=...` with one contract at a time:

   | `pipeline.run(sales_orders(FILE), schema_contract=...)` | What happens |
   |---|---|
   | `{"columns": "freeze"}` | Fails: *Can't add table column `payment_method` … because `columns` are frozen*. Nothing is loaded. |
   | `{"columns": "discard_value"}` | Loads, but drops `payment_method`. |
   | `{"data_type": "freeze"}` | Fails: *Can't add variant column `unit_price__v_text`*. |
   | `{"data_type": "discard_row"}` | Loads, but skips the line with `pris saknas`. |

   - **After a failure:** the failed load package stays pending, and dlt would retry it on the next run. Discard it before you try the next contract:
     ```powershell
     dlt -y pipeline lab_030_xlsx_schema_evolution abort-packages
     ```
   - **After a successful load:** start over with v1 as above before you try the next contract.

3. **Remove a hint.** In `COLUMNS`, change the `order_lines` entry to `{}`, then start over with v1 as in step 2. Now `unit_price` is `BIGINT`, and `29.90` lands in `unit_price__v_double`:
   - Excel stores every number the same way, and openpyxl returns `899.00` as an int but `29.90` as a float.
   - The first value decides the column's type.

   Put the hint back afterwards.

## Takeaways

- dlt types columns from the values it gets. Column hints fix what inference gets wrong.
- By default the schema evolves: new columns are added, and values that don't fit go to variant columns instead of failing the load.
- Data contracts let you freeze or discard instead. A failed run stays pending until you abort it.
