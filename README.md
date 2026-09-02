# Rideshare Dynamic Surge Pricing MLOps

End-to-end MLOps implementation for the exam case study **Rideshare Dynamic Surge Pricing Engine**.

## Architecture

```text
Synthetic/Incoming Spatial-Temporal Data
              |
              v
        Apache Airflow
              |
              v
   Data Validation + Cleaning
              |
              v
        DVC Versioning
              |
              v
     Feature Engineering
              |
              v
         Feature Store
        (CSV artifacts)
              |
              v
       Model Training
              |
              v
    Weights & Biases (W&B)
              |
              v
       Model Validation
              |
              v
        Docker + FastAPI
              |
              v
       Real-time Prediction
              |
              v
   Prometheus / Grafana Metrics
              |
              v
     Drift / Performance Check
              |
        degraded?
         /     \
       no       yes
       |         |
   continue   Airflow retraining
```

## Tools mapped to the course

- **Git**: source-code version control
- **DVC**: dataset/model artifact versioning
- **Apache Airflow**: scheduled orchestration and retraining
- **W&B**: experiment tracking, metrics and artifacts
- **Feature Store**: reusable online/offline-style feature artifacts
- **Docker**: reproducible packaging
- **FastAPI**: REST model serving
- **Prometheus**: operational/model-serving metrics
- **Grafana**: optional monitoring dashboard

These correspond to the MLOps topics in the course handout.

## Project structure

```text
rideshare-mlops/
├── app/
│   └── main.py
├── dags/
│   └── rideshare_pricing_pipeline.py
├── monitoring/
│   ├── prometheus.yml
│   └── check_drift.py
├── scripts/
│   ├── generate_data.py
│   ├── validate_data.py
│   ├── feature_engineering.py
│   ├── train.py
│   ├── validate_model.py
│   └── deploy_check.py
├── data/
│   └── raw/.gitkeep
├── features/.gitkeep
├── models/.gitkeep
├── reports/.gitkeep
├── dvc.yaml
├── params.yaml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 1. Create the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Generate initial data

```bash
python scripts/generate_data.py
```

## 3. Initialize DVC

```bash
dvc init
mkdir -p dvc_storage
dvc remote add -d local_storage ./dvc_storage
dvc add data/raw/rideshare.csv
git add data/raw/rideshare.csv.dvc .gitignore data/raw/.gitkeep
git commit -m "Add versioned rideshare dataset"
```

Then:

```bash
dvc push
```

## 4. Run the pipeline manually once

```bash
python scripts/validate_data.py
python scripts/feature_engineering.py
python scripts/train.py
python scripts/validate_model.py
```

The trained model is written to `models/surge_model.joblib`.

If W&B is configured, training metrics are logged automatically.

### W&B setup

Create a W&B account and set:

```bash
export WANDB_API_KEY="your-key"
export WANDB_PROJECT="rideshare-surge-pricing"
```

The code also supports offline mode:

```bash
export WANDB_MODE=offline
```

This is useful for a classroom demo if internet/account access is unavailable.

## 5. Start FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000/docs
```

Test:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "zone_id": 5,
    "driver_density": 8,
    "demand": 42,
    "traffic_level": 0.85,
    "rain_intensity": 0.5,
    "temperature": 27,
    "hour": 18,
    "day_of_week": 4
  }'
```

## 6. Docker

```bash
docker build -t rideshare-surge-api .
docker run --rm -p 8000:8000 rideshare-surge-api
```

## 7. Airflow

The supplied `docker-compose.yml` is intended for a local classroom demonstration.

```bash
docker compose up -d
```

Open Airflow at:

```text
http://localhost:8080
```

Default credentials in this demo:

```text
username: admin
password: admin
```

The DAG is:

```text
rideshare_surge_pricing_pipeline
```

It performs:

```text
generate -> validate -> features -> train -> validate_model -> drift_check
```

The DAG is scheduled periodically and can also be triggered manually.

## 8. Monitoring

FastAPI exposes:

```text
GET /health
GET /metrics
```

Prometheus can scrape `/metrics`.

A simple Grafana instance can be connected to Prometheus for dashboards.

## 9. Automated retraining logic

`monitoring/check_drift.py` compares the current production feature distribution with the training feature distribution.

If the drift score exceeds the configured threshold, it creates:

```text
reports/retraining_trigger.json
```

Airflow can use this signal to start the retraining branch.

For a classroom implementation, this demonstrates the required feedback loop:

```text
Monitor -> Detect degradation/drift -> Trigger retraining -> Train -> Validate -> Deploy
```

## 10. What to show during the practical/demo

1. GitHub repository and README
2. DVC-tracked dataset
3. W&B experiment dashboard
4. Airflow DAG
5. FastAPI `/docs`
6. Successful `/predict` request
7. Docker image/container
8. Prometheus `/metrics`
9. Drift/retraining trigger
10. Updated model after retraining

## Important

Do not commit `.env`, W&B API keys, generated model files, or DVC storage secrets to GitHub.
