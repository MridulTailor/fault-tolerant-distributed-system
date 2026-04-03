from fastapi import FastAPI
import logging
from datetime import datetime
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/data")
async def get_data():
    logger.info("Received request for /data at %s, hostname: %s", datetime.now(), socket.gethostname())
    return {
        "service": "B",
        "message": "Hello from Service B!",
        "hostname": socket.gethostname(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)