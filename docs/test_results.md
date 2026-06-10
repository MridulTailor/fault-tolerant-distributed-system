# Distributed System Test Results - June 10, 2026

**1. Capacity Limits (`test_capacity_limits.py`)**
Successfully allocated the exact cluster maximum of 30 sessions. The remaining 5 requests were correctly rejected with `503` errors.

**2. Concurrency / Split-Brain (`test_concurrency.py`)**
Fired 40 concurrent requests across both schedulers. Exactly 30 succeeded and 10 were rejected, proving no over-allocation occurred during simultaneous requests.

**3. Node Failure Routing (`test_node_failure.py`)**
Marked `node-1` as DOWN while generating traffic. All 5 new sessions were successfully routed to `node-2`, completely avoiding the downed node.

**4. Redis Failure / Recovery (`test_redis_failure.py`)**
Paused the Redis container, which correctly caused the system to fast-fail with a `500` error. Once unpaused, the system instantly recovered and resumed successful allocations.

**5. Idempotency (`test_idempotency.py`)**
Attempted to delete the same session twice. The first request succeeded (`200 OK`), and the second safely returned `404 Not Found` without crashing the system.

**6. Capacity Leak (`test_capacity_leak.py`)**
Created and deleted 15 sessions iteratively. The total cluster capacity correctly returned to 0 at the end of the test, proving no capacity was permanently leaked.

**7. Flapping Nodes (`test_flapping_nodes.py`)**
Rapidly toggled a node UP and DOWN every 100ms during allocation. The system gracefully handled the erratic health state and successfully allocated all 20 sessions without dropping requests.

**8. Stale Reads Defense (`test_stale_reads.py`)**
Filled the cluster to 29/30 capacity, successfully made the 30th allocation, and proved that the 31st request was instantly rejected by the atomic Lua script.

**9. High Load (`test_high_load.py`)**
Sent 200 concurrent requests across 50 worker threads against the NGINX Load Balancer. The system remained 100% stable, processing all requests in 1.70 seconds with exactly 30 successes, 170 `503` rejections, and 0 internal errors.
