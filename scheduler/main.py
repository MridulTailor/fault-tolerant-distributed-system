from fastapi import FastAPI, HTTPException
import httpx
import logging
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
import asyncpg

from config import REDIS_URL, NODE_MANAGER_URL, POSTGRES_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pg_pool = await asyncpg.create_pool(POSTGRES_URL)
    yield
    await app.state.pg_pool.close()

app = FastAPI(lifespan=lifespan)

import redis.asyncio as redis
import json

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
@app.post("/sessions")
async def create_session():
    async with httpx.AsyncClient() as client:
        # 1. Fetch nodes
        try:
            resp = await client.get(f"{NODE_MANAGER_URL}/nodes", timeout=2.0)
            resp.raise_for_status()
        except Exception as e:
            logger.error("Failed to fetch nodes: %s", e)
            raise HTTPException(status_code=500, detail="Failed to communicate with Node Manager")
            
        data = resp.json()
        nodes = data.get("nodes", [])
        
        # 2. Choose node and attempt allocation
        chosen_node_id = None
        for node in nodes:
            if not node["healthy"] or node["used"] >= node["capacity"]:
                continue
                
            node_id = node["id"]
            
            try:
                reserve_resp = await client.post(f"{NODE_MANAGER_URL}/nodes/{node_id}/allocate", timeout=2.0)
                reserve_resp.raise_for_status()
                
                resp_data = reserve_resp.json()
                if resp_data.get("success"):
                    chosen_node_id = node_id
                    break
                else:
                    logger.warning("Failed to allocate on %s: %s", node_id, resp_data.get("reason"))
                    continue # Try the next node
            except Exception as e:
                logger.error("Error calling allocate on %s: %s", node_id, e)
                continue # Try the next node
                
        if not chosen_node_id:
            raise HTTPException(status_code=503, detail="No available capacity in the cluster")
            
        # 4. Generate session and store
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        session_data = {
            "id": session_id,
            "nodeId": chosen_node_id,
            "status": "RUNNING",
            "createdAt": created_at.isoformat() + "Z"
        }
        await redis_client.hset(f"session:{session_id}", mapping=session_data)
        
        try:
            await app.state.pg_pool.execute(
                "INSERT INTO sessions_history (id, node_id, status, created_at) VALUES ($1, $2, $3, $4)",
                session_id, chosen_node_id, "RUNNING", created_at
            )
        except Exception as e:
            logger.error("Failed to log session to history: %s", e)
            
        logger.info("Session %s allocated to %s", session_id, chosen_node_id)
        
        return session_data

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    session_data = await redis_client.hgetall(f"session:{session_id}")
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
        
    node_id = session_data["nodeId"]
    
    async with httpx.AsyncClient() as client:
        try:
            release_resp = await client.post(f"{NODE_MANAGER_URL}/nodes/{node_id}/release", timeout=2.0)
            release_resp.raise_for_status()
        except Exception as e:
            logger.error("Failed to release capacity on %s for session %s: %s", node_id, session_id, e)
            # Proceed to delete session anyway for MVP
            
    await redis_client.delete(f"session:{session_id}")
    
    try:
        await app.state.pg_pool.execute(
            "UPDATE sessions_history SET status = $1, completed_at = $2 WHERE id = $3",
            "COMPLETED", datetime.utcnow(), session_id
        )
    except Exception as e:
        logger.error("Failed to update session history: %s", e)
        
    logger.info("Session %s deallocated from %s", session_id, node_id)
    return {"message": "Session deleted", "session_id": session_id}

@app.get("/sessions")
async def get_sessions():
    keys = await redis_client.keys("session:*")
    sessions = []
    for key in keys:
        session_data = await redis_client.hgetall(key)
        sessions.append(session_data)
    return {"sessions": sessions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)