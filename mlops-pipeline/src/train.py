import tempfile
from pathlib import Path

import mlflow
import mlflow.sklearn
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import argparse

def main():
    # Read the output folder path for the model.
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_output", type=str, required=True)
    args = parser.parse_args()
 
    # Load the data.
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    # Split the data into train data and test data.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train a simple model.
    n_estimators = 100
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    clf.fit(X_train, y_train)

    # Make a prediction and calculate the accuracy.
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    # Record the parameter and the metric in MLflow.
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_metric("accuracy", acc)

    # Save the model.
    # In MLflow 2.8 or later, mlflow.sklearn.log_model() calls /api/2.0/mlflow/logged-models.
    # The Azure ML tracking server does not support this API.
    # The call returns error 404.
    # Use save_model and log_artifacts.
    # These functions upload only the model artifact.
    # mlflow.sklearn.log_model(clf, artifact_path="model")
    # with tempfile.TemporaryDirectory() as tmp:
    #     model_dir = Path(tmp) / "model"
    #     mlflow.sklearn.save_model(clf, model_dir)
    #     mlflow.log_artifacts(str(model_dir), artifact_path="model")
    # Save the model under the pipeline output folder.
    model_dir = Path(args.model_output) / "model"
    mlflow.sklearn.save_model(clf, str(model_dir))

    # Keep the same model files in the MLflow run record.
    mlflow.log_artifacts(str(model_dir), artifact_path="model")

if __name__ == "__main__":
    main()

    

