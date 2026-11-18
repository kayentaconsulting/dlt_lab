"""Lab 070 · Build your own REST API pipeline.

Pick an API at https://sampleapis.com/ and describe it in `config` below: its base URL, and the
resources (endpoints) you want as tables. Instructions: pipelines/070_your_rest_api.md
"""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig

PIPELINE_NAME = "lab_070_your_rest_api"  # unique on your machine: dlt keeps its state in ~/.dlt/pipelines/<this name>
DATASET_NAME = "lab_070_your_rest_api"  # the schema in the destination that holds this pipeline's tables


@dlt.source(name="sample_api")
def sample_api():
    config: RESTAPIConfig = {
        "client": {
            # TODO 1: the base URL of the API you picked, e.g. "https://api.sampleapis.com/coffee/"
            "base_url": "https://api.sampleapis.com/<api>/",
        },
        # settings shared by all resources: sampleapis.com returns all rows in one response (no paging)
        "resource_defaults": {"endpoint": {"paginator": "single_page"}},
        # TODO 2: the resources, one per endpoint you want as a table.
        # The shortest form is the endpoint's path as a string, e.g. "hot" for .../coffee/hot.
        # Use a dict when you need more settings, as in lab 060:
        #   {"name": "iced", "endpoint": {"path": "iced"}, "primary_key": "id", "write_disposition": "merge"}
        "resources": [
        ],
    }

    if "<api>" in config["client"]["base_url"] or not config["resources"]:
        raise ValueError("Fill in TODO 1 and TODO 2 first: see pipelines/070_your_rest_api.md")

    yield from rest_api_resources(config)


if __name__ == "__main__":
    # PIPELINE: moves data from a source to a destination: extract -> normalize -> load.
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb("db/local_data.duckdb"),
        dataset_name=DATASET_NAME,
    )

    load_info = pipeline.run(sample_api())
    print(load_info)
