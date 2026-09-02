from pathlib import Path
import time
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

MODEL_PATH = Path("models/surge_model.joblib")

FEATURE_ORDER = [
    "zone_id", "driver_density", "demand", "traffic_level",
    "rain_intensity", "temperature", "hour", "day_of_week",
    "demand_driver_ratio", "peak_hour"
]

app = FastAPI(
    title="Rideshare Dynamic Surge Pricing API",
    version="1.0.0",
    description="Real-time surge pricing model serving API."
)

Instrumentator().instrument(app).expose(app)

model = None

class PredictionRequest(BaseModel):
    zone_id: int = Field(..., ge=1)
    driver_density: float = Field(..., ge=0)
    demand: float = Field(..., ge=0)
    traffic_level: float = Field(..., ge=0, le=1)
    rain_intensity: float = Field(..., ge=0, le=1)
    temperature: float
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)

@app.on_event("startup")
def load_model():
    global model
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/predict")
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not available. Train/deploy a model first."
        )

    demand_driver_ratio = request.demand / (request.driver_density + 1.0)
    peak_hour = int(17 <= request.hour <= 21)

    row = pd.DataFrame([{
        "zone_id": request.zone_id,
        "driver_density": request.driver_density,
        "demand": request.demand,
        "traffic_level": request.traffic_level,
        "rain_intensity": request.rain_intensity,
        "temperature": request.temperature,
        "hour": request.hour,
        "day_of_week": request.day_of_week,
        "demand_driver_ratio": demand_driver_ratio,
        "peak_hour": peak_hour
    }])[FEATURE_ORDER]

    prediction = float(model.predict(row)[0])
    prediction = max(1.0, min(3.0, prediction))

    return {
        "surge_multiplier": round(prediction, 3),
        "model": "surge_model",
        "feature_source": "precomputed/online feature-store concept"
    }
