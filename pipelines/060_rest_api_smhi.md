# 060 · Bonus: REST API (SMHI weather data)

**Goal:** load data from a web API with dlt's ready-made REST API source, including a parent/child pair of endpoints.

Needs internet access to `opendata-download-metobs.smhi.se`.

## dlt concepts

| Concept | In this lab |
|---------|----------------|
| REST API source | `rest_api_resources(config)`: you describe the API in a dict, and dlt makes the requests. |
| Parent/child resources | `temperature_observations` calls one endpoint per station, filling `{resources.stations.id}` from the parent. |
| `include_from_parent` | Copies the station `id` onto every observation, as `_stations_id`. |
| `processing_steps` | Filters rows before they're loaded. Here, only active stations are kept. |
| `response_actions` | Decides what to do with certain responses. Here a 404, from a station with no data for the last day, is skipped instead of failing the run. |
| `merge` + `primary_key` | A rerun updates existing rows instead of adding duplicates. dlt uses a `_staging` schema for this. |
| Child table | The nested `link` list in each station becomes the table `stations__link`. |

## The data

The API returns JSON. One station looks like this (shortened):

```json
{
  "key": "188800",
  "name": "Abisko",
  "id": 188800,
  "latitude": 68.3538,
  "active": false,
  "link": [
    {"href": ".../station/188800.json", "rel": "station", "type": "application/json"},
    {"href": ".../station/188800.xml",  "rel": "station", "type": "application/xml"}
  ]
}
```

`link` is a list, so dlt can't store it in a single column. It becomes a child table instead.

## Run

```powershell
python pipelines/060_rest_api_smhi.py
```

A run takes a few seconds. It loads every active station (about 230), and the last day of hourly temperatures for each one (about 4,400 rows). The few stations without data for the last day are skipped.

## Explore

In `db/db_explore.ipynb`:

```python
q("select id, name, latitude, height from lab_060_rest_api_smhi.stations")
```

To join a station to its links, use `_dlt_id` → `_dlt_parent_id`:

```python
q("""
select s.name, sl.type, sl.href
from lab_060_rest_api_smhi.stations as s
join lab_060_rest_api_smhi.stations__link as sl on s._dlt_id = sl._dlt_parent_id
""")
```

To join observations to stations, use `_stations_id`. `date` is in milliseconds since 1970, and `value` is text:

```python
q("""
select s.name, count(*) as observations, round(avg(t.value::double), 1) as avg_temp
from lab_060_rest_api_smhi.temperature_observations as t
join lab_060_rest_api_smhi.stations as s on t._stations_id = s.id
group by 1 order by avg_temp
""")
```

## Try this

1. **Run it again.** The row counts barely change: `merge` on the primary key updates rows instead of duplicating them. Only new hourly observations are added. Compare that with `append` in lab 010.
2. **Look at the last run** from the terminal: `dlt pipeline lab_060_rest_api_smhi trace`. It shows how long each step took and how many rows went into each table.
3. **Check the types.** `value` is `VARCHAR`, because SMHI sends temperatures as strings, for example `"4.2"`. dlt stores what it receives. Lab 030 covers types.

## Takeaways

- dlt's REST API source turns an API description into resources. You don't write any request code.
- Nested lists become child tables, linked back with `_dlt_parent_id` → `_dlt_id`.
- `merge` with a `primary_key` makes reruns safe: rows are updated, not duplicated.
