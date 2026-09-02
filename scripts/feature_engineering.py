from pathlib import Path
import pandas as pd
import numpy as np

FEATURES = [
    "zone_id", "driver_density", "demand", "traffic_level",
    "rain_intensity", "temperature", "hour", "day_of_week",
    "demand_driver_ratio", "peak_hour"
]

def main():
    Path("features").mkdir(exist_ok=True)

    df = pd.read_csv("data/raw/rideshare.csv")

    df["demand_driver_ratio"] = df["demand"] / (df["driver_density"] + 1.0)
    df["peak_hour"] = df["hour"].between(17, 21).astype(int)

    feature_df = df[FEATURES + ["surge_multiplier"]].copy()
    feature_df.to_csv("features/pricing_features.csv", index=False)

    print(f"Feature store updated: {len(feature_df)} rows.")
    print("Features:", ", ".join(FEATURES))

if __name__ == "__main__":
    main()
