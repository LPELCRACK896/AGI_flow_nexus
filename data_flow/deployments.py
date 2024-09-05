from prefect import flow


if __name__ == "__main__":

    # Example
    flow.from_source(
        source="https://github.com/prefecthq/demo.git",
        entrypoint="flow.py:my_flow",
    ).deploy(
        name="test-managed-flow",
        work_pool_name="my-managed-pool",
    )