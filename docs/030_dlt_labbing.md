# 030 · dlt labbing

How to work with dlt in this repo. The instructions for each lab are in its `.md` in [`pipelines/`](../pipelines/).

## Run everything from the repo root

dlt reads `.dlt/config.toml` and `.dlt/secrets.toml` from the **current directory**. If you run a pipeline from another folder, dlt runs without them and doesn't warn you. The database path `db/local_data.duckdb` is also relative to the current directory.

```powershell
cd C:\dev\dlt_lab
.venv\Scripts\Activate.ps1
```

dlt looks for each setting in this order and uses the first match:

1. Environment variables: `SECTION__KEY` in upper case, e.g. `RUNTIME__LOG_LEVEL=INFO`
2. `.dlt/` in the current directory
3. `.dlt/` in your home folder (`~/.dlt/`)

## The lab loop

1. **Read** the lab's `.md` in `pipelines/`.
2. **Look** at the sample file it loads in `data/`. Which tables do you expect?
3. **Run** the pipeline.
4. **Explore** the result in `db/db_explore.ipynb`.
5. **Change** something (the data, or a setting in the pipeline) and run again.

## Run a pipeline

```powershell
python pipelines/<file>.py
```

With uv: `uv run python pipelines/<file>.py`.

A run has three steps:

| Step | What happens |
|------|--------------|
| **Extract** | Reads the data from the source |
| **Normalize** | Infers the schema and flattens nested data into tables |
| **Load** | Writes the tables to DuckDB |

A successful run ends with `Load package … is LOADED and contains no failed jobs`.

## Explore the data

Open `db/db_explore.ipynb`, select the `.venv` kernel and run all cells. Then query with `q("select …")`.

- Each pipeline's `dataset_name` is a schema, so you query `select * from <dataset_name>.<table>`.
- "Schema" means two things in dlt. The **dataset** is a schema in the database, a namespace for tables. The **dlt schema** describes those tables (columns, types, hints and contracts) and is named after the source, so `@dlt.source(name="sales_orders")` gives a schema named `sales_orders`. `dlt pipeline <name> schema` prints the dlt schema, `_dlt_version` stores each version of it, and lab 030 changes it.
- dlt adds tables (`_dlt_loads`, `_dlt_version`, `_dlt_pipeline_state`) and columns (`_dlt_load_id`, `_dlt_id`) to track what was loaded and when.
- DuckDB allows only one writer at a time. `q()` closes its connection after every query. If a pipeline still fails with a lock error, restart the notebook kernel.

## dlt commands

`<name>` is the `pipeline_name` set in the script, not the file name.

| Command | What it does |
|---------|--------------|
| `dlt --version` | Shows the installed dlt version |
| `dlt pipeline --list-pipelines` | Lists the pipelines that have run on this machine |
| `dlt pipeline <name> info` | Shows the pipeline's state, schemas and resources |
| `dlt pipeline <name> trace` | Shows the steps, row counts and timings of the last run |
| `dlt pipeline <name> schema` | Prints the inferred schema (`--format mermaid` for a diagram) |
| `dlt pipeline <name> failed-jobs` | Shows the errors from failed loads |
| `dlt -y pipeline <name> abort-packages` | Discards a load package that failed, so the next run starts from new data |
| `dlt --help`, `dlt pipeline --help` | Lists everything else |

The labs set the DuckDB path in their code, and the CLI can't see it. So commands that change the database, such as `dlt pipeline <name> drop`, fail here. Use `refresh` in the code instead (see [Start over](#start-over)).

## Where dlt keeps its working files

`~/.dlt/pipelines/<name>/` (on Windows `C:\Users\<you>\.dlt\pipelines\<name>\`) holds the pipeline's state, schemas, load packages and last trace. Every project on your machine shares this folder, so pipeline names must be unique.

## Start over

Delete the database **and** the pipeline's working folder. If you delete only the database, dlt still remembers its state, for example how far an incremental load got.

```powershell
Remove-Item -Force db\local_data.duckdb
Remove-Item -Recurse -Force $HOME\.dlt\pipelines\<name>
```

```bash
rm -f db/local_data.duckdb
rm -rf ~/.dlt/pipelines/<name>
```

To start just one lab over, run its pipeline once with `pipeline.run(..., refresh="drop_sources")`. dlt drops that lab's tables and schema, then loads fresh.

---

[← 020 Project outline](020_project_outline.md)
