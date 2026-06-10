# Fault-Tolerant Distributed System

A small microservices demo showing retries, load balancing, and reverse proxy routing with FastAPI, Docker Compose, and NGINX.

## Architecture

![System Architecture](docs/architecture.png)

## Circuit Breaker / Resilience Flow

![Circuit Breaker Flow](docs/circuit-breaker.png)

## Services

- Gateway (`8000`): Aggregates data from Scheduler and Node Manager.
- Scheduler (`8001`, replica on `8003`): Responds to `/data` and is load-balanced by NGINX.
- Node Manager (`8002`): Responds to `/data`.
- NGINX (`80`): Reverse proxy for internal service-to-service calls.

## Run

```bash
docker compose up --build
```

## Try It

- Main API (aggregated response):

```bash
curl http://localhost:8000/data
```

- Through NGINX routes:

```bash
curl http://localhost/scheduler/data
curl http://localhost/node-manager/data
```

## Fault-Tolerance Features

- Retry with exponential backoff in Gateway for upstream calls.
- Retryable handling for transient failures.
- NGINX upstream pool for Scheduler replicas.

## Stop

```bash
docker compose down
```
