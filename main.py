```python
from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import threading
import uuid

app = FastAPI()

class Resource(BaseModel):
    id: str
    type: str
    status: str = "available"
    allocated_to: Optional[str] = None

resource_pool = {}
resource_locks = {}

@app.post("/resources")
def add_resource(resource_type: str):
    resource_id = str(uuid.uuid4())
    resource = Resource(id=resource_id, type=resource_type)
    resource_pool[resource_id] = resource
    resource_locks[resource_id] = threading.Lock()
    return {"message": "Resource added", "id": resource_id}

@app.get("/resources")
def list_resources():
    return list(resource_pool.values())

@app.get("/resources/available")
def available_resources():
    return [r for r in resource_pool.values() if r.status == "available"]

@app.post("/request")
def request_resource(resource_type: str, requester_id: str):
    for res_id, res in resource_pool.items():
        if res.type == resource_type and res.status == "available":
            lock = resource_locks[res_id]
            if lock.acquire(blocking=False):
                try:
                    if res.status == "available":
                        res.status = "allocated"
                        res.allocated_to = requester_id
                        return {"message": "Allocated", "resource_id": res.id}
                finally:
                    lock.release()
    raise HTTPException(404, "No available resource")

@app.post("/release")
def release_resource(resource_id: str):
    if resource_id not in resource_pool:
        raise HTTPException(404, "Resource not found")
    lock = resource_locks[resource_id]
    lock.acquire()
    try:
        res = resource_pool[resource_id]
        if res.status != "allocated":
            raise HTTPException(400, "Not allocated")
        res.status = "available"
        res.allocated_to = None
    finally:
        lock.release()
    return {"message": "Released", "id": resource_id}
