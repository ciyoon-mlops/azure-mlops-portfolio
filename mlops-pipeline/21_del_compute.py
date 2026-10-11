from azure_config import compute_name, create_ml_client

ml_client = create_ml_client()

ml_client.compute.begin_delete(compute_name()).result()
