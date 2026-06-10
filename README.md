# Distributed Scheduler

A fault-tolerant workload scheduler that allocates sessions across a cluster of nodes. It demonstrates strict service boundaries, atomic capacity enforcement, and load-balanced routing with FastAPI, Docker Compose, and NGINX.

## Architecture

The system is composed of three microservices:

- **Node Manager (`8002`)**: Owns the definitive state of the nodes (health and capacity). It exposes internal endpoints to allocate and release node capacity atomically.
- **Scheduler (`8001`, replica on `8003`)**: Handles placement logic and session state. It queries the Node Manager to find healthy nodes with available capacity, secures the reservation, and tracks the session in memory. It is load-balanced by NGINX.
- **Gateway (`8000`)**: A stateless public API proxy that forwards session requests (`POST`, `DELETE`, `GET`) to the internal Schedulers.

## Run

```bash
docker compose up --build
```

## Try It

- **Create a Session (Allocate a Node)**:
```bash
curl -X POST http://localhost:8000/sessions
```
*(Returns the generated `session_id` and the assigned `node_id`)*

- **List Active Sessions**:
```bash
curl http://localhost:8000/sessions
```

- **View Node State**:
```bash
curl http://localhost:8002/nodes
```

- **Simulate Node Failure**:
```bash
curl -X POST http://localhost:8002/nodes/node-1/down
```
*(New sessions will automatically route to other healthy nodes)*

- **Delete a Session (Release Capacity)**:
```bash
curl -X DELETE http://localhost:8000/sessions/<session_id>
```

## Fault-Tolerance & Distributed System Features

- **Strict Ownership**: Node Manager is the sole atomic source of truth for capacity, preventing race conditions.
- **Resilient Retry Logic**: If multiple Schedulers try to allocate the same node concurrently and one fails due to capacity constraints, the Scheduler gracefully catches the rejection and retries placement on the next available node.
- **Health-Aware Routing**: Schedulers actively filter out nodes that have been marked as unhealthy.
- **NGINX Load Balancing**: API traffic to the Scheduler is round-robin distributed across multiple replicas.

## Stop

```bash
docker compose down
```
