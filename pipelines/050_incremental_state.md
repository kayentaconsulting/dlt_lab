# 050 · Incremental loading and state: only new files are loaded

**Goal:** read daily order files from a folder with dlt's filesystem source, load only the files that are new since the last run, and see where dlt keeps track of what it has loaded.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| Filesystem source | `filesystem(bucket_url=..., file_glob="*.csv")` lists the files in a folder. It yields file items, not rows. The same code reads a bucket (`s3://`, `az://`, `gs://`); lab 060 reads MinIO. |
| Transformer | `read_orders` takes the file items and yields their rows, with `file_name` on every row. `files \| read_orders` connects the two. |
| Incremental | `dlt.sources.incremental("file_name", last_value_func=max)`: dlt remembers the highest file name it has loaded. The next run only passes on files whose name sorts after it. With `min`, it remembers the lowest name and only earlier files pass. |
| Pipeline state | Where that cursor is kept: locally in `~/.dlt/pipelines/<name>/state.json`, and in the destination table `_dlt_pipeline_state`. That's why it can be restored. |

## The data

Daily order files in `data/050_incremental_state/`, named by date:

| Folder | Files |
|--------|-------|
| `incoming/` | `orders_2026-11-16.csv` (2 orders), `orders_2026-11-17.csv` (3 orders). This is the folder the pipeline reads. |
| `later/` | `orders_2026-11-18.csv` (the next day) and `orders_2026-11-15.csv` (a file that arrives late). You move these into `incoming/` during the lab. |

## Run

```powershell
python pipelines/050_incremental_state.py
```

This loads 5 orders from the 2 files. Run it again: the output says `0 load package(s) were loaded`, because there are no new files.

## Explore

In `db/db_explore.ipynb`:

```python
q("select * from lab_050_incremental_state.orders order by order_id")
q("select file_name, _dlt_load_id, count(*) as orders from lab_050_incremental_state.orders group by 1, 2 order by 1")
```

## Try this

1. **A new day arrives.** Move the next day's file into `incoming/` (or drag it in Explorer), then run:
   ```powershell
   Move-Item data\050_incremental_state\later\orders_2026-11-18.csv data\050_incremental_state\incoming\
   ```
   Only `orders_2026-11-18.csv` is loaded, under a new `_dlt_load_id`. The two older files aren't read again.

2. **Find the state, then delete it locally.**
   - `dlt pipeline lab_050_incremental_state info -v` shows the cursor under `sources › sales_orders › resources › filesystem › incremental`: `"last_value": "orders_2026-11-18.csv"`.
   - The same state is in the destination: `q("select version, created_at from lab_050_incremental_state._dlt_pipeline_state")`.
   - Now delete the local working folder and run again:
     ```powershell
     Remove-Item -Recurse -Force $HOME\.dlt\pipelines\lab_050_incremental_state
     ```
     Nothing is loaded again: dlt found no local state, restored it from `_dlt_pipeline_state` and carried on where it was. This is what lets a pipeline move to another machine.
   - **If both exist**, `pipeline.run()` compares their versions before it extracts anything. The version is a counter that goes up each time the state changes. The destination's state wins if its version is the same or higher. The local one wins only when it has changes that haven't been loaded yet, for example after a failed load. And if the dataset is missing from the destination, dlt resets the local state instead. (`pipeline.extract()` on its own doesn't check the destination.)

3. **A late file.** Move `later\orders_2026-11-15.csv` into `incoming/` and run. Nothing is loaded:
   - `orders_2026-11-15.csv` sorts before `orders_2026-11-18.csv`, so the cursor skips it.
   - The choice of cursor decides what counts as new. In a bucket like MinIO you'd usually use `modification_date`, the upload time. Here the file names are used because they work the same on every machine, and copying a file keeps its old modification date.
   - To load it anyway, reset the state: run once with `pipeline.run(sales_orders(), refresh="drop_sources")`. All 4 files are loaded.

   Afterwards, move the two files back to `later/` so the lab starts the same way next time.

## Takeaways

- The filesystem source lists files, and a transformer reads them. The same code works on a local folder and on S3/MinIO.
- An incremental cursor makes reruns cheap: only new files are read.
- The state is kept both locally and in the destination, so it survives a lost working folder or a new machine.
