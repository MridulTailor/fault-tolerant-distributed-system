from fastapi import FastAPI
import logging
from datetime import datetime
import random
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/data")
async def get_data():
    logger.info("Received request for /data at %s", datetime.now())

    # Simulate random failures
    if random.random() < 0.3:  # 30% chance of failure
        logger.error("Simulated failure in Scheduler at %s", datetime.now())
        raise HTTPException(status_code=500, detail="Simulated failure in Scheduler")
    else:
        logger.info("Successfully processed request in Scheduler at %s", datetime.now())
        return {"service": "Scheduler", "message": "Hello from Scheduler!"}

'''
Write new APIs
POST /allocate
Input:

{
  "sessionId": "123"
}

Output:

{
  "nodeId": "node-2"
}

Maintain in-memory node capacity first.
'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)