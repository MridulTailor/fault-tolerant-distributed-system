# Distributed Scheduler

A workload scheduler that allocates sessions across a cluster of nodes. It demonstrates strict service boundaries, atomic capacity enforcement, and load-balanced routing with FastAPI, Docker Compose, and NGINX.

## Motivation

This project is deeply inspired by the technical challenges faced by cloud gaming platform **NVIDIA GeForce NOW**. When thousands of players simultaneously request access to a game, the backend infrastructure must instantly assign each player to a dedicated, high-performance GPU server. 

Building such a system requires a scheduler that is incredibly fast, completely fault-tolerant, and capable of handling massive concurrency.

## Use Cases

Although inspired by cloud gaming architectures, this pattern applies to any high-throughput, session-based workload distribution:
- AI inference workloads
- Render jobs
- Video encoding
- CI/CD runners
- Batch processing
- Distributed scraping

## Architecture

![Architecture Diagram](docs/architecture.png)

The system is composed of five core components:
- **Redis (`6379`)**: Centralized, fast operational state store that tracks real-time node capacity and active sessions.
- **PostgreSQL (`5433`)**: Database that tracks the lifecycle of all sessions (creation and completion) without cluttering the operational state.
- **Node Manager (`8002`)**: Owns the logic for the nodes. It exposes internal endpoints to allocate and release node capacity atomically via Redis Lua scripts.
- **Scheduler (`8001`, replica on `8003`)**: Handles placement logic and session routing. It queries the Node Manager to find healthy nodes, secures the reservation, stores the active session in Redis, and asynchronously logs the lifecycle event to PostgreSQL. It is load-balanced by NGINX.
- **Gateway (`8000`)**: A stateless public API proxy that forwards session requests (`POST`, `DELETE`, `GET`) to the internal Schedulers.

## Scheduling Strategies
- **Least Loaded (Default)**: Chooses the node with the lowest utilization. Spreads load evenly but increases fragmentation.
- **Most Available Capacity**: Chooses the node with the highest absolute free slots.
- **Best Fit**: Chooses the smallest node that can still fit the workload. Tightly packs sessions and minimizes fragmentation.
- **Random**: A pure baseline strategy that randomly selects any healthy node with capacity.

## Benchmark Results

I built a custom in-memory benchmarking framework (`benchmark/run.py`) to simulate high-throughput traffic and evaluate these strategies on actual metrics.

Here are the results of simulating **10,000 sessions** across a **1,000-node** cluster:

```text
Strategy                  Utilization     Fragmentation   Rejected  
-----------------------------------------------------------------
Random                     83.5%          Medium          0         
Least Loaded               79.5%          High            0         
Most Available Capacity    75.4%          High            0         
Best Fit                  100.0%          Low             0         
```

## Run

First, set up your environment variables:
```bash
cp .env.example .env
```

Then, start the cluster:
```bash
docker compose up --build -d
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
- **Strict Separation of Concerns**: Fast operational state (active sessions, node capacity) is kept strictly isolated in Redis, while historical session lifecycle data is safely archived in PostgreSQL.
- **Centralized Distributed State**: Schedulers are completely stateless; all active sessions are globally tracked in a shared Redis cluster, allowing seamless horizontal scaling.
- **Atomic Lua Script Allocations**: Node Manager uses an atomic Redis Lua script to read capacity and increment usage in a single, un-interruptible operation. This prevents "split-brain" over-allocation race conditions even under heavy concurrent load.
- **Resilient Retry Logic**: If multiple Schedulers try to allocate the same node concurrently and one fails due to capacity constraints (caught by the Lua script), the Scheduler gracefully catches the rejection and retries placement on the next available node.
- **Health-Aware Routing**: Schedulers actively filter out nodes that have been marked as unhealthy.
- **NGINX Load Balancing**: API traffic to the Scheduler is round-robin distributed across multiple replicas.

## Stop

```bash
docker compose down
```
## How I used AI in building this project: 
- Writing tests
- Generate System Architecture Diagram
- Refactoring code for clean architecture and better performance
- Adding documentation