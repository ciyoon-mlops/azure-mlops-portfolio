import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def main():
    # Read the output folder path from the train step.
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_input", type=str, required=True)
    args = parser.parse_args()

    # Read the model from the model folder in the output folder.
    model_dir = Path(args.model_input) / "model"
    model = mlflow.sklearn.load_model(str(model_dir))

    # Use the same data split as train.py.
    # train.py used the train data.
    # This file uses the test data.
    iris = datasets.load_iris()
    _, X_test, _, y_test = train_test_split(
        iris.data,
        iris.target,
        test_size=0.2,
        random_state=42,
    )

    # Make a prediction with the saved model.
    # Do not train the model again.
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Save the accuracy in the run record of the evaluation step.
    mlflow.log_metric("eval_accuracy", float(accuracy))
    print(f"eval_accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()
    