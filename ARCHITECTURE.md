# Architecture

```text
                    +----------------------+
                    | Traffic / Weather /  |
                    | Demand / Drivers     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      Airflow         |
                    | Schedule/Orchestrate |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Validate + Clean     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | DVC                  |
                    | Dataset Versioning   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Feature Engineering  |
                    | Feature Store        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Model Training       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | W&B                  |
                    | Experiments/Metrics  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Model Validation     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Docker               |
                    | Model Packaging      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | FastAPI              |
                    | REST Model Serving   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Rideshare App        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Prometheus/Grafana   |
                    | Monitoring            |
                    +----------+-----------+
                               |
                       Drift/Degradation
                               |
                               v
                           Airflow
                         Retraining
```
