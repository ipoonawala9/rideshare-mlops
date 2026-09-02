from pathlib import Path
import json
import joblib
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

def main():
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    model_path = Path("models/surge_model.joblib")
    if not model_path.exists():
        raise FileNotFoundError(model_path)

    df = pd.read_csv("features/pricing_features.csv")
    X = df.drop(columns=["surge_multiplier"])
    y = df["surge_multiplier"]

    _, X_test, _, y_test = train_test_split(
        X, y,
        test_size=params["model"]["test_size"],
        random_state=params["model"]["random_state"]
    )

    model = joblib.load(model_path)
    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5

    threshold = params["thresholds"]["max_mae"]

    result = {
        "mae": float(mae),
        "rmse": float(rmse),
        "max_allowed_mae": float(threshold),
        "status": "PASS" if mae <= threshold else "FAIL"
    }

    Path("reports").mkdir(exist_ok=True)
    Path("reports/model_validation.json").write_text(json.dumps(result, indent=2))

    print(result)

    if result["status"] != "PASS":
        raise SystemExit("Model validation failed.")

if __name__ == "__main__":
    main()
