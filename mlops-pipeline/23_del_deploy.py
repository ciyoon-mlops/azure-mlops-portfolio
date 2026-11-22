from azure_config import create_ml_client

ml_client = create_ml_client()

# Delete the endpoint and its deployments after testing.
ml_client.online_endpoints.begin_delete(
    name="iris-thomas-20261024"
).result()

print("Endpoint deletion completed.")



