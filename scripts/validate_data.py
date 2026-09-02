from pathlib import Path
import pandas as pd

REQUIRED = [
    "zone_id", "driver_density", "demand", "traffic_level",
    "rain_intensity", "temperature", "hour", "day_of_week",
    "surge_multiplier"
]

def main():
    path = Path("data/raw/rideshare.csv")
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)

    missing_columns = [c for c in REQUIRED if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    if df[REQUIRED].isnull().any().any():
        raise ValueError("Validation failed: missing values found.")

    if (df["driver_density"] < 0).any():
        raise ValueError("Validation failed: negative driver density.")

    if (df["demand"] < 0).any():
        raise ValueError("Validation failed: negative demand.")

    if not df["traffic_level"].between(0, 1).all():
        raise ValueError("Validation failed: traffic_level must be 0..1.")

    if not df["rain_intensity"].between(0, 1).all():
        raise ValueError("Validation failed: rain_intensity must be 0..1.")

    if not df["hour"].between(0, 23).all():
        raise ValueError("Validation failed: invalid hour.")

    if not df["day_of_week"].between(0, 6).all():
        raise ValueError("Validation failed: invalid day_of_week.")

    print(f"Validation passed: {len(df)} rows.")

if __name__ == "__main__":
    main()
