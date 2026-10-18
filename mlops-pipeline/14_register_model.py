"""Register the Iris model from a training step output.

Run this file from the mlops-pipeline directory.
The command is python 14_register_model.py.
The script uses the latest completed train step in AZURE_EXPERIMENT_NAME.
Pass --train-job-name to register a specific training step.
"""

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import Model

from azure_config import create_ml_client, experiment_name


def is_completed(status) -> bool:
    value = getattr(status, "value", status)
    return str(value).lower() == "completed"


def is_train_step(step) -> bool:
    if step.display_name == "train_step":
        return True
    properties = getattr(step, "properties", None) or {}
    return properties.get("azureml.moduleName") == "iris_train"


def created_at(job) -> datetime:
    created = getattr(getattr(job, "creation_context", None), "created_at", None)
    if created is not None:
        return created
    return datetime.min.replace(tzinfo=timezone.utc)


def latest_train_job_name(ml_client) -> str:
    # Pick the newest completed pipeline in this experiment.
    experiment = experiment_name()
    pipelines = [
        job
        for job in ml_client.jobs.list()
        if job.experiment_name == experiment
        and job.type == "pipeline"
        and is_completed(job.status)
    ]
    if not pipelines:
        raise RuntimeError(f"No completed pipeline job in experiment {experiment}.")

    pipeline_job = max(pipelines, key=created_at)
    for step in ml_client.jobs.list(parent_job_name=pipeline_job.name):
        if is_train_step(step) and is_completed(step.status):
            print(f"Pipeline job: {pipeline_job.name}")
            return step.name

    raise RuntimeError(
        f"No completed train step in pipeline {pipeline_job.name}."
    )


def download_model_directory(ml_client, train_job_name: str) -> Path:
    # A datastore path to this output fails MLflow model validation.
    # Download the output and register the folder that contains MLmodel.
    download_dir = Path(__file__).resolve().parent / "downloaded_model"
    if download_dir.exists():
        shutil.rmtree(download_dir)

    ml_client.jobs.download(
        name=train_job_name,
        output_name="model_output",
        download_path=str(download_dir),
    )

    mlmodel_files = list(download_dir.rglob("MLmodel"))
    if len(mlmodel_files) != 1:
        raise FileNotFoundError(
            f"Expected one MLmodel file under {download_dir}, "
            f"found {len(mlmodel_files)}."
        )
    return mlmodel_files[0].parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train-job-name",
        default=None,
        help="Training step job name. The default is the latest completed train step.",
    )
    args = parser.parse_args()

    ml_client = create_ml_client()
    train_job_name = args.train_job_name or latest_train_job_name(ml_client)
    print(f"Training job: {train_job_name}")

    model_dir = download_model_directory(ml_client, train_job_name)
    print(f"MLmodel directory: {model_dir}")

    model = Model(
        name="iris-random-forest",
        path=str(model_dir),
        type=AssetTypes.MLFLOW_MODEL,
        description="Iris classifier from the train-evaluate pipeline.",
        tags={
            "source_train_job": train_job_name,
        },
    )
    registered_model = ml_client.models.create_or_update(model)

    print(f"Model name: {registered_model.name}")
    print(f"Model version: {registered_model.version}")
    print(f"Model type: {registered_model.type}")
    print(f"Model ID: {registered_model.id}")


if __name__ == "__main__":
    main()
