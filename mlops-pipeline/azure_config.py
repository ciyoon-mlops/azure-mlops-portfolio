"""Load Azure ML workspace and job settings from environment / .env."""

from __future__ import annotations

import os
from pathlib import Path

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

_DIR = Path(__file__).resolve().parent
_ENV_PATH = _DIR / ".env"
_ENV_EXAMPLE = _DIR / ".env.example"
load_dotenv(_ENV_PATH)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise EnvironmentError(
            f"Missing required environment variable: {name}. "
            f"Copy {_ENV_EXAMPLE} to {_ENV_PATH} and set the value."
        )
    return value.strip()


def create_ml_client() -> MLClient:
    return MLClient(
        DefaultAzureCredential(),
        subscription_id=require_env("AZURE_SUBSCRIPTION_ID"),
        resource_group_name=require_env("AZURE_RESOURCE_GROUP"),
        workspace_name=require_env("AZURE_WORKSPACE_NAME"),
    )


def compute_name() -> str:
    return require_env("AZURE_COMPUTE_NAME")


def compute_size() -> str:
    return require_env("AZURE_COMPUTE_SIZE")


def compute_min_instances() -> int:
    return int(require_env("AZURE_COMPUTE_MIN_INSTANCES"))


def compute_max_instances() -> int:
    return int(require_env("AZURE_COMPUTE_MAX_INSTANCES"))


def compute_idle_seconds() -> int:
    return int(require_env("AZURE_COMPUTE_IDLE_SECONDS"))


def ml_environment() -> str:
    return require_env("AZURE_ML_ENVIRONMENT")


def experiment_name() -> str:
    return require_env("AZURE_EXPERIMENT_NAME")


def job_display_name() -> str:
    return require_env("AZURE_JOB_DISPLAY_NAME")


def training_code_path() -> str:
    return str(Path(__file__).resolve().parent / "src")
