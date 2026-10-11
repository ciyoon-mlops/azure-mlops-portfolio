from azure.ai.ml.entities import AmlCompute

from azure_config import (
    compute_idle_seconds,
    compute_max_instances,
    compute_min_instances,
    compute_name,
    compute_size,
    create_ml_client,
)

ml_client = create_ml_client()

compute = AmlCompute(
    name=compute_name(),
    size=compute_size(),
    min_instances=compute_min_instances(),
    max_instances=compute_max_instances(),
    idle_time_before_scale_down=compute_idle_seconds(),
)

ml_client.compute.begin_create_or_update(compute).result()
