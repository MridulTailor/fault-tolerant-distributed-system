# Distributed Scheduler

A fault-tolerant workload scheduler that allocates sessions across a cluster of nodes. It demonstrates strict service boundaries, atomic capacity enforcement, and load-balanced routing with FastAPI, Docker Compose, and NGINX.

## Architecture

The system is composed of four core components:

- **Redis (`6379`)**: The centralized, distributed state store that persists session data and tracks real-time node capacity and health.
- **Node Manager (`8002`)**: Owns the logic for the nodes. It exposes internal endpoints to allocate and release node capacity atomically via Redis Lua scripts, completely preventing split-brain scheduling.
- **Scheduler (`8001`, replica on `8003`)**: Handles placement logic and session routing. It queries the Node Manager to find healthy nodes, secures the reservation, and stores the session state globally in Redis. It is load-balanced by NGINX.
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

- **Centralized Distributed State**: Schedulers are completely stateless; all active sessions are globally tracked in a shared Redis cluster, allowing seamless horizontal scaling.
- **Atomic Lua Script Allocations**: Node Manager uses an atomic Redis Lua script to read capacity and increment usage in a single, un-interruptible operation. This prevents "split-brain" over-allocation race conditions even under heavy concurrent load.
- **Resilient Retry Logic**: If multiple Schedulers try to allocate the same node concurrently and one fails due to capacity constraints (caught by the Lua script), the Scheduler gracefully catches the rejection and retries placement on the next available node.
- **Health-Aware Routing**: Schedulers actively filter out nodes that have been marked as unhealthy.
- **NGINX Load Balancing**: API traffic to the Scheduler is round-robin distributed across multiple replicas.

## Stop

```bash
docker compose down
```
