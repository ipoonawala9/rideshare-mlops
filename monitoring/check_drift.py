from pathlib import Path
import json
import numpy as np
import pandas as pd
import yaml

NUMERIC_FEATURES = [
    "driver_density", "demand", "traffic_level",
    "rain_intensity", "temperature", "demand_driver_ratio"
]

def normalized_mean_difference(a, b):
    pooled = (np.std(a) + np.std(b)) / 2 + 1e-8
    return abs(np.mean(a) - np.mean(b)) / pooled

def main():
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    training = pd.read_csv("features/pricing_features.csv")

    # Demo: production data can be supplied through this file.
    production_path = Path("data/production/current_features.csv")

    if not production_path.exists():
        result = {
            "status": "NO_PRODUCTION_DATA",
            "drift_score": 0.0,
            "retraining_required": False
        }
    else:
        production = pd.read_csv(production_path)
        scores = [
            normalized_mean_difference(training[c], production[c])
            for c in NUMERIC_FEATURES
        ]
        drift_score = float(np.mean(scores))
        threshold = params["thresholds"]["drift_score"]

        result = {
            "status": "DRIFT_CHECKED",
            "drift_score": drift_score,
            "threshold": threshold,
            "retraining_required": drift_score > threshold
        }

    Path("reports").mkdir(exist_ok=True)
    Path("reports/retraining_trigger.json").write_text(
        json.dumps(result, indent=2)
    )

    print(result)

if __name__ == "__main__":
    main()
