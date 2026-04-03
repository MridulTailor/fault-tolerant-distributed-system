from fastapi import FastAPI
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/data")
async def get_data_from_services():
    async with httpx.AsyncClient() as client:
        response_b = await client.get("http://nginx/service-b/data", timeout=10.0)
        response_c = await client.get("http://nginx/service-c/data", timeout=10.0)

        # error handling
        if response_b.status_code != 200:
            logger.error("Failed to get data from Service B: %s", response_b.text)
            return {"error": "Failed to get data from Service B"}
        if response_c.status_code != 200:
            logger.error("Failed to get data from Service C: %s", response_c.text)
            return {"error": "Failed to get data from Service C"}

        #log
        logger.info("Received data from Service B: %s", response_b.json())
        logger.info("Received data from Service C: %s", response_c.json())

        #return
        return {
            "service": "A",
            "message": "Hello from Service A!",
            "data_from_b": response_b.json(),
            "data_from_c": response_c.json(),
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)