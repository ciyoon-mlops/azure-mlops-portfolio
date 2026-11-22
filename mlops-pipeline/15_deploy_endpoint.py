from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
)

from azure_config import create_ml_client


# Connect to the existing Azure ML workspace.
ml_client = create_ml_client()

# latest is the most recently registered version of this model.
registered_model = ml_client.models.get(
    name="iris-random-forest",
    label="latest",
)

print(f"Model ID: {registered_model.id}")
print(f"Model name: {registered_model.name}")
print(f"Model version: {registered_model.version}")

# Set a distinctive endpoint name.
endpoint_name ="iris-thomas-20261024"

# Define the endpoint. This does not create it in Azure yet.
endpoint = ManagedOnlineEndpoint(
    name=endpoint_name,
    description="Online inference endpoint for the Iris classifier.",
    auth_mode="key"
)

# Define the deployment. This does not create Azure resources yet.
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name=endpoint_name,
    model=registered_model.id,
    # Dsv6, Dsv7, and DSv4 are not online-endpoint SKUs. DSv2 is end of life.
    # D4as_v4 is supported and needs 8 DASv4 cores. This subscription's limit is 10.
    instance_type="Standard_D4as_v4",
    instance_count=1,
)


# Create the endpoint in Azure and wait for completion.
created_endpoint = ml_client.online_endpoints.begin_create_or_update(
    endpoint
).result()

# Print the endpoint status.
print(f"Endpoint name: {created_endpoint.name}")
print(f"Endpoint state: {created_endpoint.provisioning_state}")

# Create the deployment and wait for completion.
# Azure provisions a VM and prepares the model environment.
print("Creating deployment: blue")

created_deployment = (
    ml_client.online_deployments.begin_create_or_update(
        deployment
    ).result()
)

print(f"Deployment name: {created_deployment.name}")
print(f"Deployment state: {created_deployment.provisioning_state}")


# Route all endpoint requests to the blue deployment.
endpoint.traffic = {"blue": 100}

updated_endpoint = (
    ml_client.online_endpoints.begin_create_or_update(
        endpoint
    ).result()
)

print(f"Endpoint state: {updated_endpoint.provisioning_state}")
print(f"Traffic: {updated_endpoint.traffic}")
