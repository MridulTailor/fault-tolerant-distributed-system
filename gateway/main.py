from fastapi import FastAPI
import httpx
import logging
import asyncio
import circuit_breaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

breaker_scheduler = circuit_breaker.CircuitBreaker(threshold=4, timeout=30)
breaker_node_manager = circuit_breaker.CircuitBreaker(threshold=4, timeout=30)

@app.get("/data")
async def get_data_from_services():
    async with httpx.AsyncClient() as client:
        response_scheduler = await retry_request("http://nginx/scheduler/data", client, breaker=breaker_scheduler)
        if response_scheduler is None:
            return {"error": "Failed to connect to Scheduler"}
        response_node_manager = await retry_request("http://nginx/node-manager/data", client, breaker=breaker_node_manager)
        if response_node_manager is None:
            return {"error": "Failed to connect to Node Manager"}

        logger.info("Received data from Scheduler: %s", response_scheduler.json())
        logger.info("Received data from Node Manager: %s", response_node_manager.json())

        return {
            "service": "Gateway",
            "message": "Hello from Gateway!",
            "data_from_scheduler": response_scheduler.json(),
            "data_from_node_manager": response_node_manager.json(),
        }

async def retry_request(url, client, retries=3, delay=1, breaker=None):
    for attempt in range(retries):
        if breaker and not breaker.allow_request():
            logger.warning("Circuit breaker is OPEN for %s. Skipping request.", url)
            return None
        try:
            response = await client.get(url, timeout=2.0)
            response.raise_for_status()  # Raise an exception for HTTP errors
            if breaker:
                breaker.record_success()
            return response
        except httpx.RequestError as e:
            logger.warning("Attempt %d: Failed to connect to %s: %s", attempt + 1, url, str(e))
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error("Attempt %d: HTTP error from %s: %s", attempt + 1, url, str(e))
            if status_code < 500:
                if breaker:
                    breaker.record_failure()
                return None  # Don't retry for client errors
        if attempt < retries - 1:
            await asyncio.sleep(delay * (2 ** attempt))  # Wait before retrying
           
    logger.error("Failed to connect to %s after %d attempts", url, retries)
    if breaker:
        breaker.record_failure()
    return None

'''
Write new APIs
POST /sessions
DELETE /sessions/:id
GET /sessions

'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)