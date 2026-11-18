# 070 · Build your own REST API pipeline

**Goal:** build a pipeline for an API you choose, starting from a template. You describe the API in a config dict, and dlt makes the requests, creates the tables and unpacks nested data.

Needs internet access to `api.sampleapis.com`.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| `client.base_url` | The part of the URL that all endpoints share, e.g. `https://api.sampleapis.com/coffee/`. |
| `resources` | The endpoints you want as tables. A string such as `"hot"` is the endpoint's path and the table's name. A dict adds settings: `name`, `endpoint.path`, `primary_key`, `write_disposition`, `processing_steps`. |
| `resource_defaults` | Settings shared by all resources. The template sets `"paginator": "single_page"`, because sampleapis.com returns all rows in one response. |
| Default write disposition | `append`: running twice loads every row twice, unless you set a `primary_key` and `merge` (lab 040). |

## Build it

1. **Pick an API** at [sampleapis.com](https://sampleapis.com/) and open one of its endpoints in the browser, e.g. `https://api.sampleapis.com/coffee/hot`. You see a JSON list, and every item becomes a row.
2. **TODO 1** in `pipelines/070_your_rest_api.py`: set `base_url` to the API's URL, e.g. `"https://api.sampleapis.com/coffee/"`.
3. **TODO 2**: add the endpoint to `resources` as a string, e.g. `"hot"`.
4. **Run:**
   ```powershell
   python pipelines/070_your_rest_api.py
   ```
   Until both TODOs are filled in, the script stops with `Fill in TODO 1 and TODO 2 first`.

## Explore

In `db/db_explore.ipynb`, list your tables, then look at one. Replace `hot` with your resource's name:

```python
q("select table_name from information_schema.tables where table_schema = 'lab_070_your_rest_api'")
q("select * from lab_070_your_rest_api.hot")
```

Nested data is unpacked as in lab 020:
- A list becomes a child table. Coffee's `ingredients` becomes `hot__ingredients`, with each ingredient in the column `value`.
- An object becomes `__` columns. Beer's `rating` becomes `rating__average` and `rating__reviews`.

## Try this

1. **Add a second endpoint** of the same API to `resources`, e.g. `"iced"`, and run. Each resource becomes its own table.
2. **Run twice, then fix the duplicates.**
   - Run again: every row is now there twice, because the default is `append`.
   - Change the resource to the dict form: `{"name": "hot", "endpoint": {"path": "hot"}, "primary_key": "id", "write_disposition": "merge"}`.
   - Start over once with `pipeline.run(sample_api(), refresh="drop_sources")`, then run without `refresh` as often as you like: the row count stays the same.
3. **Filter rows** with `processing_steps`, as in lab 060. For example, only coffees that contain espresso:
   `"processing_steps": [{"filter": lambda row: "Espresso" in row["ingredients"]}]` (9 of the 20 hot coffees).

## Stuck?

A complete config for the coffee API:

```python
"client": {"base_url": "https://api.sampleapis.com/coffee/"},
"resource_defaults": {"endpoint": {"paginator": "single_page"}},
"resources": [
    "hot",
    {"name": "iced", "endpoint": {"path": "iced"}, "primary_key": "id", "write_disposition": "merge"},
],
```

## Takeaways

- With dlt's REST API source, a pipeline is mostly configuration: a base URL and a list of resources.
- Strings are enough to get started. Dicts add keys, write dispositions and processing steps when you need them.
- Nested JSON from an API is unpacked into child tables and `__` columns, exactly like a JSON file.
