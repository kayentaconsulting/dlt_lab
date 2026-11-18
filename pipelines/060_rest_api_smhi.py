"""Lab 060 (bonus) · REST API: SMHI weather stations and temperatures.

Loads data from SMHI's open API, so it needs internet. Instructions: pipelines/060_rest_api_smhi.md
"""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig

PIPELINE_NAME = 'lab_060_rest_api_smhi'  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = 'lab_060_rest_api_smhi'  # the schema in DuckDB that holds the tables

# SOURCE: the REST API source builds one resource per endpoint described in the config below.
@dlt.source(name='smhi', section='smhi')
def smhi_source():
    smhi_config: RESTAPIConfig = {
        "client": {
            # the API's base URL; each resource below adds its own path
            "base_url":"https://opendata-download-metobs.smhi.se/api/version/latest"
        },

        # settings shared by all resources: every endpoint returns all its data in one response (no paging)
        "resource_defaults": {"endpoint": {"paginator": "single_page"}},

        # each resource becomes a table
        "resources": [
            {   # parent resource: one row per weather station
                "name":"stations",
                "endpoint": {"path": "parameter/2.json", "data_selector": "station"},
                # processing step: drop inactive stations before they're loaded
                "processing_steps": [{"filter": lambda stations: stations["active"]}],
                # merge on the primary key: a rerun updates stations instead of duplicating them
                "primary_key": "id",
                "write_disposition": "merge",
            },

            {   # child resource: temperature observations, one request per station
                "name": "temperature_observations",
                "endpoint": {
                    "path": (
                        # {resources.stations.id} is filled in from each row of the parent resource
                        "parameter/1/station/{resources.stations.id}"
                        "/period/latest-day/data.json"  # SMHI periods: latest-hour, latest-day, latest-months
                    ),
                    # the rows are in the response's "value" list
                    "data_selector": "value",
                    # some stations have no data for the last day and answer 404: skip them instead of failing
                    "response_actions": [{"status_code": 404, "action": "ignore"}],
                },
                # copies the parent's id onto every row (as _stations_id) to link back to stations
                "include_from_parent": ["id"],
                "primary_key": ["_stations_id", "date"],
                "write_disposition": "merge",
            }
        ],
    }

    yield from rest_api_resources(smhi_config)

# run only when the file is executed as a script, not when it's imported (e.g. by Airflow)
if __name__ == "__main__":
    # PIPELINE: moves the data from the source to the destination: extract -> normalize -> load
    pipeline = dlt.pipeline(
        pipeline_name = PIPELINE_NAME,
        dataset_name = DATASET_NAME,
        # all labs load into the same DuckDB file; the path is relative to the repo root
        destination = dlt.destinations.duckdb("db/local_data.duckdb"),
        progress= "log"  # print extract/normalize/load progress while the pipeline runs
    )

    load_info = pipeline.run(smhi_source())

    print(load_info)
