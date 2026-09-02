from pathlib import Path
import os
import joblib
import pandas as pd
import yaml
import wandb

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

def main():
    Path("models").mkdir(exist_ok=True)

    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    df = pd.read_csv("features/pricing_features.csv")

    X = df.drop(columns=["surge_multiplier"])
    y = df["surge_multiplier"]

    test_size = params["model"]["test_size"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=params["model"]["random_state"]
    )

    run = wandb.init(
        project=os.getenv("WANDB_PROJECT", "rideshare-surge-pricing"),
        entity=os.getenv("WANDB_ENTITY") or None,
        config=params["model"],
        mode=os.getenv("WANDB_MODE", "online"),
        job_type="train",
    )

    model = RandomForestRegressor(
        n_estimators=params["model"]["n_estimators"],
        max_depth=params["model"]["max_depth"],
        random_state=params["model"]["random_state"],
        n_jobs=-1,
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    wandb.log({
        "validation_mae": mae,
        "validation_rmse": rmse,
        "training_rows": len(X_train),
        "validation_rows": len(X_test),
    })

    model_path = "models/surge_model.joblib"
    joblib.dump(model, model_path)

    artifact = wandb.Artifact("surge-pricing-model", type="model")
    artifact.add_file(model_path)
    run.log_artifact(artifact)

    run.finish()

    print(f"Model saved: {model_path}")
    print(f"MAE={mae:.4f}, RMSE={rmse:.4f}")

if __name__ == "__main__":
    main()
