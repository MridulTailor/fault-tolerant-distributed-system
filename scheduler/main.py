from fastapi import FastAPI, HTTPException
import httpx
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# In-memory session store (MVP)
sessions = {}

@app.post("/sessions")
async def create_session():
    async with httpx.AsyncClient() as client:
        # 1. Fetch nodes
        try:
            resp = await client.get("http://node-manager:8002/nodes", timeout=2.0)
            resp.raise_for_status()
        except Exception as e:
            logger.error("Failed to fetch nodes: %s", e)
            raise HTTPException(status_code=500, detail="Failed to communicate with Node Manager")
            
        data = resp.json()
        nodes = data.get("nodes", [])
        
        # 2. Choose node (first available healthy node)
        chosen_node = None
        for node in nodes:
            if node["healthy"] and node["used"] < node["capacity"]:
                chosen_node = node
                break
                
        if not chosen_node:
            raise HTTPException(status_code=503, detail="No available capacity in the cluster")
            
        node_id = chosen_node["id"]
        
        # 3. Reserve capacity
        try:
            reserve_resp = await client.post(f"http://node-manager:8002/nodes/{node_id}/allocate", timeout=2.0)
            reserve_resp.raise_for_status()
        except Exception as e:
            logger.error("Failed to reserve capacity on %s: %s", node_id, e)
            raise HTTPException(status_code=500, detail="Failed to reserve capacity")
            
        # 4. Generate session and store
        session_id = str(uuid.uuid4())
        sessions[session_id] = node_id
        logger.info("Session %s allocated to %s", session_id, node_id)
        
        return {"session_id": session_id, "node_id": node_id}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    node_id = sessions[session_id]
    
    async with httpx.AsyncClient() as client:
        try:
            release_resp = await client.post(f"http://node-manager:8002/nodes/{node_id}/release", timeout=2.0)
            release_resp.raise_for_status()
        except Exception as e:
            logger.error("Failed to release capacity on %s for session %s: %s", node_id, session_id, e)
            # Proceed to delete session anyway for MVP
            
    del sessions[session_id]
    logger.info("Session %s deallocated from %s", session_id, node_id)
    return {"message": "Session deleted", "session_id": session_id}

@app.get("/sessions")
async def get_sessions():
    return {"sessions": [{"session_id": k, "node_id": v} for k, v in sessions.items()]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)