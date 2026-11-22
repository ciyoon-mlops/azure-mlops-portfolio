import json
import tempfile

from azure_config import create_ml_client


# Connect to the existing Azure ML workspace.
ml_client = create_ml_client()

endpoint_name = "iris-thomas-20261024"

# One Iris flower: sepal length, sepal width, petal length, petal width.
payload = {
    "input_data": [
        [5.1, 3.5, 1.4, 0.2],
    ]
}

# The invoke API reads the request from a file.
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as request_file:
    json.dump(payload, request_file)
    request_path = request_file.name

response = ml_client.online_endpoints.invoke(
    endpoint_name=endpoint_name,
    deployment_name="blue",
    request_file=request_path,
)

print(f"Endpoint name: {endpoint_name}")
print(f"Response: {response}")
