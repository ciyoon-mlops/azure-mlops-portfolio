"""Submit an Azure ML pipeline with one training step.

Run this file from the project root.
The project root contains azure_config.py and the src folder.
The required files are azure_config.py and src/train.py.
The command is python submit_pipeline.py.
This code does not register the model.
This code does not include an evaluate step.
"""

from pathlib import Path

from azure.ai.ml import command, dsl, Output, Input

from azure_config import (
    compute_name,
    create_ml_client,
    experiment_name,
    ml_environment,
)


def main():
    # Check the code folder.
    # Stop the submission if the train file is missing.
    code_dir = Path(__file__).resolve().parent / "src"
    if not (code_dir / "train.py").is_file():
        raise FileNotFoundError(f"Train file not found: {code_dir / 'train.py'}")

    # Create the workspace client from the current settings.
    ml_client = create_ml_client()

    # Define the training job.
    # Do not start training now.
    # code is the code folder to upload to Azure ML.
    # command is the command to run on the compute.
    # environment holds the packages and the runtime for training.
    # compute is the compute name for training.
    train_component = command(
        name="iris_train",
        display_name="Iris training",
        code=str(code_dir),
        command="python train.py --model_output ${{outputs.model_output}}",
        outputs={
            "model_output": Output(type="uri_folder"),
        },
        environment=ml_environment(),
        compute=compute_name(),
    )

    # Define the job that receives the model folder and evaluates the model.
    evaluate_component = command(
        name="iris_evaluate",
        display_name="Iris evaluation",
        code=str(code_dir),
        command="python evaluate.py --model_input ${{inputs.model_input}}",
        inputs={
            "model_input": Input(type="uri_folder")
        },
        environment=ml_environment(),
        compute=compute_name(),
    )    

    # Convert the function into a pipeline definition.
    @dsl.pipeline(description="Train the Iris model in a single-step pipeline")
    def training_pipeline():
        # Add the training job as a pipeline step.
        # This line looks like a Python function call.
        # This call builds the run structure.
        train_step = train_component()
        # Connect the training output to the evaluation input.
        evaluate_step = evaluate_component(
            model_input=train_step.outputs.model_output
        )

    # Create the pipeline job.
    # Do not submit it to Azure now.
    pipeline_job = training_pipeline()

    # Submit the pipeline to the workspace.
    # experiment_name groups the run records.
    returned_job = ml_client.jobs.create_or_update(
        pipeline_job,
        experiment_name=experiment_name(),
    )
    print(f"Pipeline submitted: {returned_job.name}")
    if returned_job.studio_url:
        print(f"Studio URL: {returned_job.studio_url}")

    # Show the run logs.
    # Wait until the run ends.
    ml_client.jobs.stream(returned_job.name)

    # Get the final pipeline status.
    final_job = ml_client.jobs.get(returned_job.name)
    print(f"Pipeline status: {final_job.status}")

    # Get the status of each step.
    for step in ml_client.jobs.list(parent_job_name=returned_job.name):
        print(f"Step: {step.display_name or step.name}, status: {step.status}")

    # In Studio, check the accuracy and the model artifact of the train step.
    # This pipeline does not yet have an output that passes the model between steps.
    # Add model_output and an evaluate step in the next exercise.
    # After the run, check the compute node count and Cost Management.
    # min_instances=0 is a compute setting.
    # This file does not change that setting.


if __name__ == "__main__":
    main()
