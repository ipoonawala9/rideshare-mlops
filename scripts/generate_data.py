from pathlib import Path
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 5000

def main():
    Path("data/raw").mkdir(parents=True, exist_ok=True)

    zone = RNG.integers(1, 21, N)
    hour = RNG.integers(0, 24, N)
    day = RNG.integers(0, 7, N)

    driver_density = np.clip(RNG.normal(18, 7, N), 2, 40)
    demand = np.clip(
        25
        + 18 * ((hour >= 17) & (hour <= 21))
        + 0.35 * (20 - driver_density)
        + RNG.normal(0, 7, N),
        1,
        None,
    )
    traffic = np.clip(
        0.25
        + 0.45 * ((hour >= 8) & (hour <= 10))
        + 0.55 * ((hour >= 17) & (hour <= 21))
        + RNG.normal(0, 0.12, N),
        0,
        1,
    )
    rain = np.clip(RNG.beta(2, 6, N), 0, 1)
    temperature = RNG.normal(27, 5, N)

    surge = (
        1.0
        + 0.025 * demand
        - 0.018 * driver_density
        + 0.55 * traffic
        + 0.35 * rain
        + 0.08 * ((hour >= 17) & (hour <= 21))
        + RNG.normal(0, 0.08, N)
    )
    surge = np.clip(surge, 1.0, 3.0)

    df = pd.DataFrame({
        "zone_id": zone,
        "driver_density": driver_density.round(3),
        "demand": demand.round(3),
        "traffic_level": traffic.round(3),
        "rain_intensity": rain.round(3),
        "temperature": temperature.round(3),
        "hour": hour,
        "day_of_week": day,
        "surge_multiplier": surge.round(3),
    })

    df.to_csv("data/raw/rideshare.csv", index=False)
    print(f"Generated {len(df)} rideshare observations.")

if __name__ == "__main__":
    main()
