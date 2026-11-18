# dlt lab

A hands-on lab for [dlt](https://dlthub.com/docs) (data load tool), the open-source Python library for loading data.

The pipelines in `pipelines/` are numbered labs. Each one shows a dlt feature by loading a small sample file (.csv, .json, .xlsx, .xml) into a local DuckDB database in `db/`, which you then explore in `db/db_explore.ipynb`. In lab 070 you build your own REST API pipeline from a template. The last lab is a MinIO (S3) → SQL Server template that you adapt to your own environment. **Every other lab runs as-is, with no credentials.**

## Docs

| # | Doc | Covers |
|---|-----|--------|
| 010 | [Install](docs/010_install.md) | IT checklist, setting up Python on Windows / WSL / macOS / Linux or with uv, troubleshooting |
| 020 | [Project outline](docs/020_project_outline.md) | What each folder and file is for |
| 030 | [dlt labbing](docs/030_dlt_labbing.md) | Running pipelines, exploring the data, dlt commands, starting over |

New here? Start with [010 Install](docs/010_install.md), then work through the labs in [`pipelines/`](pipelines/).
