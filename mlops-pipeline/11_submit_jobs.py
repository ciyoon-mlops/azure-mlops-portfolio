from azure.ai.ml import Output, command

from azure_config import (
    compute_name,
    create_ml_client,
    experiment_name,
    job_display_name,
    ml_environment,
    training_code_path,
)

ml_client = create_ml_client()

job = command(
    code=training_code_path(),
    command="python train.py --model_output ${{outputs.model_output}}",
    outputs={
        "model_output": Output(type="uri_folder"),
    },
    environment=ml_environment(),
    compute=compute_name(),
    experiment_name=experiment_name(),
    display_name=job_display_name(),
)

created_job = ml_client.jobs.create_or_update(job)

print("Job name:", created_job.name)
print("Studio URL:", created_job.studio_url)

ml_client.jobs.stream(created_job.name)
