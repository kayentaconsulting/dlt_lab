# 020 · Project outline

```text
dlt_lab/
├── README.md          Start page, links to the docs
├── docs/              These guides, numbered in reading order
├── pipelines/         The labs: numbered pipeline scripts + a .md with each lab's instructions
├── data/              Sample files, one folder per lab
├── db/                The DuckDB database + db_explore.ipynb
├── .dlt/              dlt configuration
├── pyproject.toml     Dependencies (uv)
├── uv.lock            Locked dependency versions (uv)
├── requirements.txt   The same locked versions, for pip
└── .venv/             Your virtual environment (created in 010, not in git)
```

## `pipelines/`

The labs, worked through in number order. Each lab `NNN_<topic>` has two files:

| File | |
|------|---|
| `NNN_<topic>.md` | The lab's instructions: start here. |
| `NNN_<topic>.py` | The pipeline. Run it from the repo root. |

Each pipeline loads into its own schema in `db/local_data.duckdb`: its `dataset_name`, e.g. `lab_010_csv_basics`. Two labs are templates that you complete yourself:
- 070, where you build your own REST API pipeline;
- the last lab, a MinIO (S3) → SQL Server template that needs credentials.

All other labs run as-is.

## `data/`

Small, readable sample files (.csv, .json, .xlsx, .xml), one folder per lab: `data/NNN_<topic>/`. Open them before you load them. Pipelines only read these files and never change them.

## `db/`

| File | |
|------|---|
| `local_data.duckdb` | The database every lab loads into. Each pipeline's `dataset_name` becomes a schema. Created on the first run and not in git: delete it to start over. |
| `db_explore.ipynb` | Notebook for querying the database. |

## `.dlt/`

| File | |
|------|---|
| `config.toml` | Settings for all pipelines (log level, telemetry). In git. |
| `secrets.toml` | Credentials. Not in git. Only the last lab needs it. |
| `secrets.toml.example` | Template: copy it to `secrets.toml` and fill it in. |

dlt finds this folder from the current directory, so always run from the repo root ([030](030_dlt_labbing.md#run-everything-from-the-repo-root)).

## Root files

`pyproject.toml` and `uv.lock` define the dependencies. `requirements.txt` is generated from them for pip; see [010 › For maintainers](010_install.md#for-maintainers).

## Outside the repo

`~/.dlt/pipelines/<pipeline_name>/` (on Windows `C:\Users\<you>\.dlt\pipelines\<pipeline_name>\`) is dlt's working folder for each pipeline. See [030](030_dlt_labbing.md#where-dlt-keeps-its-working-files).

---

[← 010 Install](010_install.md) · [030 dlt labbing →](030_dlt_labbing.md)
