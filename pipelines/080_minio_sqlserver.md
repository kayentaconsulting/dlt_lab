# 080 · Template: files from MinIO into SQL Server

**Goal:** load CSV files from your on-prem MinIO into SQL Server. It's lab 050's pipeline pointed at a bucket and a real database. This is the only lab that needs credentials, and every connection detail lives in `.dlt/secrets.toml`.

## dlt concepts

| Concept | In this lab |
|---------|-------------|
| Secrets | dlt reads `.dlt/secrets.toml`: `[sources.filesystem]` for MinIO and `[destination.mssql.credentials]` for SQL Server. The code holds no connection details, and `secrets.toml` stays out of git. |
| Filesystem source on S3 | `bucket_url = "s3://..."` plus an `endpoint_url` makes lab 050's code read MinIO. |
| `modification_date` cursor | In a bucket, this is the upload time: a file counts as new when it was uploaded after the last run. (Lab 050 used file names.) |
| mssql destination | Connects with pyodbc through "ODBC Driver 18 for SQL Server", using a SQL login. `dataset_name` becomes a schema. |

## What you need

| From | What |
|------|------|
| MinIO | Its S3 API address (`endpoint_url`), a bucket and folder, and an access key and secret key that can read it. If MinIO uses https with a certificate from your company's own CA, you also need that CA as a PEM file. |
| SQL Server | Host, database, and a SQL login (username and password) that may create a schema and tables. dlt doesn't use Windows authentication. |
| Your machine | ODBC Driver 18 for SQL Server, and network access to both servers. |

## Set up

1. Copy the example and replace every `<...>` placeholder:
   ```powershell
   Copy-Item .dlt\secrets.toml.example .dlt\secrets.toml
   ```
2. Upload the two files in `data/050_incremental_state/incoming/` to your bucket folder, for example in MinIO's web console.

Until every setting is filled in, the script stops and lists the ones that are missing.

## Run

```powershell
python pipelines/080_minio_sqlserver.py
```

This loads 5 orders into `lab_080_minio_sqlserver.orders`.

## Check in SQL Server

In SSMS or VS Code's SQL Server (mssql) extension:

```sql
select * from lab_080_minio_sqlserver.orders;
select * from lab_080_minio_sqlserver._dlt_loads;
```

## Try this

1. **Upload a new file.** Upload `data/050_incremental_state/later/orders_2026-11-18.csv` to the same folder and run again. Only that file is loaded.
2. **Look at the cursor:** `dlt pipeline lab_080_minio_sqlserver info -v`. Its `last_value` is the upload time of the newest file.
3. **Start over:** `dlt -y pipeline lab_080_minio_sqlserver drop --drop-all`. It drops the table and resets the cursor, so the next run loads every file again. Unlike in the DuckDB labs, the CLI can reach the database here, because the credentials are in `secrets.toml`.

## Troubleshooting

| Message | Fix |
|---------|-----|
| `Fill in .dlt/secrets.toml first … Missing: …` | Fill in the settings the message lists. |
| `SSL validation failed … CERTIFICATE_VERIFY_FAILED` | MinIO's certificate comes from your company's own CA. Get the CA as a PEM file from IT, and set `client_kwargs = { verify = "C:/certs/company-ca.pem" }` under `[sources.filesystem]`. |
| `S3 API Requests must be made to API port` | `endpoint_url` points at MinIO's web console. Use the S3 API port (often 9000). |
| `SignatureDoesNotMatch` | The secret key doesn't match the access key. |
| `0 load package(s) were loaded`, with no error, on the first run | No files were found. Check the bucket and folder in `bucket_url`, and that the files end in `.csv`. |
| `SSL Provider: … certificate verify failed` | SQL Server's certificate isn't trusted. Ask IT to make it trusted. On test servers only, set `query = { TrustServerCertificate = "yes" }`. |
| `Login failed for user …` | Wrong username or password, or the login has no access to that database. |
| `The specified driver … is not supported`, or `Data source name not found` | Install ODBC Driver 18 for SQL Server (IT), and check the `driver` line. |

## Optional: faster loads with ADBC

At millions of rows, INSERT statements get slow. dlt can bulk-copy into SQL Server through an ADBC driver instead, and it switches by itself once the driver is installed, so the code doesn't change:

```powershell
python -m pip install "dlt[parquet]" adbc-driver-manager dbc
dbc install mssql
```

Check with IT first: Columnar's mssql driver is closed source, and `dbc` sends a machine identifier with its requests.

## Takeaways

- Moving from a local folder to a bucket is configuration, not code: lab 050's pipeline reads MinIO once `bucket_url` and the credentials are set.
- All connection details live in `.dlt/secrets.toml`, out of the code and out of git.
- In a bucket, the upload time (`modification_date`) is the natural incremental cursor.
