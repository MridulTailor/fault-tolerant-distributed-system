from fastapi import FastAPI
import httpx
import logging
import asyncio
import circuit_breaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

breaker_b = circuit_breaker.CircuitBreaker(threshold=4, timeout=30)
breaker_c = circuit_breaker.CircuitBreaker(threshold=4, timeout=30)

@app.get("/data")
async def get_data_from_services():
    async with httpx.AsyncClient() as client:
        response_b = await retry_request("http://nginx/service-b/data", client, breaker=breaker_b)
        if response_b is None:
            return {"error": "Failed to connect to Service B"}
        response_c = await retry_request("http://nginx/service-c/data", client, breaker=breaker_c)
        if response_c is None:
            return {"error": "Failed to connect to Service C"}

        logger.info("Received data from Service B: %s", response_b.json())
        logger.info("Received data from Service C: %s", response_c.json())

        return {
            "service": "A",
            "message": "Hello from Service A!",
            "data_from_b": response_b.json(),
            "data_from_c": response_c.json(),
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
                return None  # Don't retry for client errors
        if attempt < retries - 1:
            await asyncio.sleep(delay * (2 ** attempt))  # Wait before retrying
           
    logger.error("Failed to connect to %s after %d attempts", url, retries)
    if breaker:
        breaker.record_failure()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)