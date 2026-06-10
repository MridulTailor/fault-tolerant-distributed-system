from fastapi import FastAPI, HTTPException, Request, Response
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

SCHEDULER_URL = "http://nginx/scheduler"

@app.post("/sessions")
async def create_session(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{SCHEDULER_URL}/sessions", timeout=5.0)
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
        except Exception as e:
            logger.error("Error communicating with scheduler: %s", e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(f"{SCHEDULER_URL}/sessions/{session_id}", timeout=5.0)
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
        except Exception as e:
            logger.error("Error communicating with scheduler: %s", e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/sessions")
async def get_sessions():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{SCHEDULER_URL}/sessions", timeout=5.0)
            return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
        except Exception as e:
            logger.error("Error communicating with scheduler: %s", e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)