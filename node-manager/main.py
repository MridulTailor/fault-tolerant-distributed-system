from fastapi import FastAPI
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/data")
async def get_data():
    logger.info("Received request for /data at %s", datetime.now())
    return {
        "service": "Node Manager",
        "message": "Hello from Node Manager!",
    }
'''
Node Manager

Owns:

GET /nodes
POST /nodes/:id/down
POST /nodes/:id/up

Stores node state.

Example:

{
  "id": "node-1",
  "capacity": 10,
  "used": 3,
  "healthy": true
}
'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)