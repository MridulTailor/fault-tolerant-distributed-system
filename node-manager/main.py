from fastapi import FastAPI, HTTPException
import logging
from datetime import datetime
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# Initial in-memory state
nodes = {
    "node-1": {"id": "node-1", "capacity": 10, "used": 0, "healthy": True},
    "node-2": {"id": "node-2", "capacity": 10, "used": 0, "healthy": True},
    "node-3": {"id": "node-3", "capacity": 10, "used": 0, "healthy": True},
}

@app.get("/nodes")
async def get_nodes():
    return {"nodes": list(nodes.values())}

@app.post("/nodes/{node_id}/down")
async def mark_node_down(node_id: str):
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    nodes[node_id]["healthy"] = False
    return nodes[node_id]

@app.post("/nodes/{node_id}/up")
async def mark_node_up(node_id: str):
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    nodes[node_id]["healthy"] = True
    return nodes[node_id]

@app.post("/nodes/{node_id}/allocate")
async def allocate_node(node_id: str):
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    node = nodes[node_id]
    if not node["healthy"]:
        raise HTTPException(status_code=400, detail="Node is not healthy")
    if node["used"] >= node["capacity"]:
        raise HTTPException(status_code=400, detail="Node is at full capacity")
    
    node["used"] += 1
    return node

@app.post("/nodes/{node_id}/release")
async def release_node(node_id: str):
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    node = nodes[node_id]
    if node["used"] > 0:
        node["used"] -= 1
    return node

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)