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
        "service": "C",
        "message": "Hello from Service C!",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)