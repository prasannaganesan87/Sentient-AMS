import os
import sys
import json
import time
import subprocess
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_FILE = "jobs_db.json"

VALID_STATUSES = ["RUNNING", "ON_HOLD", "FAILED", "SUCCESSFUL", "FINISHED"]

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return "Error while connecting to Job database"

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

app = FastAPI(title="Jobs Management API")

class StatusUpdateRequest(BaseModel):
    status: str

@app.get("/jobs/{job_id}/status")
def get_job_status(job_id: str):
    db = load_db()
    if job_id not in db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "status": db[job_id]["status"]}

@app.put("/jobs/{job_id}/status")
def update_job_status(job_id: str, req: StatusUpdateRequest):
    db = load_db()
    if job_id not in db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    new_status = req.status.upper()
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
    
    # Update the mock DB
    db[job_id]["status"] = new_status
    save_db(db)
    
    return {"message": f"SUCCESS: Job {job_id} status updated.", "new_status": new_status}

@app.get("/jobs/{job_id}/log")
def get_job_log(job_id: str):
    db = load_db()
    if job_id not in db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "log": db[job_id]["log"]}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("Starting Jobs FastAPI Backend on http://localhost:8001")
    print("="*50 + "\n")
    # Running on port 8001 to avoid conflicting with fastapi_app.py which is on 8000
    uvicorn.run(app, host="0.0.0.0", port=8001)
