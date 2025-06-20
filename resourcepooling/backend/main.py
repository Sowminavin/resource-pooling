# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 14:56:21 2025

@author: OHS1COB
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import queue
import threading
import time

# Define the resource class (e.g., database connection, file handler, etc.)
class Resource:
    def __init__(self, id: int):
        self.id = id
        self.active = False

    def reset(self):
        self.active = False
        print(f"Resource {self.id} has been reset.")

class ResourcePool:
    def __init__(self, max_size: int):
        # Initialize the pool with max_size resources
        self._pool = queue.Queue(max_size)
        for i in range(max_size):
            self._pool.put(Resource(i))  # Fill the pool with resources
        self._lock = threading.Lock()
        
    def acquire(self, timeout: float = 5.0):
        """Acquires a resource from the pool, blocking for 'timeout' seconds."""
        try:
            # Try to get a resource from the pool (removes it from the pool temporarily)
            resource = self._pool.get(timeout=timeout)
            
            # Reset the resource before returning it (clean its state)
            resource.reset()  
            
            # Mark the resource as in use
            resource.active = True
            
            # Return the resource to the caller
            return resource
        except queue.Empty:
            # If no resource is available within the timeout, raise a TimeoutError
            raise TimeoutError("No resources available within the timeout")

    def release(self, resource: Resource):
        """Releases a resource back to the pool."""
        # Mark the resource as inactive (it’s no longer in use)
        resource.active = False
        
        # Put the resource back into the pool (making it available again)
        self._pool.put(resource)

    def available(self):
        """Returns the number of available resources in the pool."""
        return self._pool.qsize()

    def add_resource(self):
        """Adds a new resource to the pool."""
        # Get the next available resource ID
        new_id = self._pool.qsize() + 1
        new_resource = Resource(new_id)
        
        # Add the new resource to the pool
        self._pool.put(new_resource)
        
        return new_resource

# Initialize the FastAPI app and resource pool
app = FastAPI()
resource_pool = ResourcePool(max_size=3)  # Max 3 resources in the pool

# Define the resource acquisition request body
class ResourceRequest(BaseModel):
    timeout: float = 5.0  # Timeout for acquiring a resource (default: 5 seconds)

# Endpoint to acquire a resource
@app.post("/acquire/")
async def acquire_resource(request: ResourceRequest):
    try:
        resource = resource_pool.acquire(timeout=request.timeout)
        return {"message": f"Resource {resource.id} acquired successfully!"}
    except TimeoutError:
        raise HTTPException(status_code=409, detail="No resources available within timeout")

# Endpoint to release a resource back to the pool
@app.post("/release/")
async def release_resource(resource_id: int):
    try:
        # Try to find the resource in the pool
        resources = list(resource_pool._pool.queue)  # Direct access for simplicity
        resource = next((res for res in resources if res.id == resource_id and res.active), None)
        
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found or already released")
        
        resource_pool.release(resource)
        return {"message": f"Resource {resource.id} released back to the pool."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint to check the number of available resources
@app.get("/available/")
async def available_resources():
    available = resource_pool.available()
    return {"available_resources": available}


# New endpoint to add a resource to the pool
@app.post("/add_resource/")
async def add_resource():
    new_resource = resource_pool.add_resource()
    return {"message": f"Resource {new_resource.id} added to the pool."}
