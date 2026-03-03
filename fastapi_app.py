from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AIMS Mock API")

# Mock database for PeopleSoft users
USER_DB = {
    "jdoe": {"status": "LOCKED", "failed_attempts": 3, "password": "old_password"},
    "msmith": {"status": "ACTIVE", "failed_attempts": 0, "password": "forgotten_password"},
    "user": {"status": "LOCKED", "failed_attempts": 5, "password": "random_password"}
}

class UnlockRequest(BaseModel):
    user_id: str

class ResetRequest(BaseModel):
    user_id: str

@app.get("/users/{user_id}")
def get_user_status(user_id: str):
    if user_id not in USER_DB:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = USER_DB[user_id].copy()
    user_data["user_id"] = user_id
    return user_data

@app.post("/api/peoplesoft/unlock")
def unlock_account(req: UnlockRequest):
    if req.user_id not in USER_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the mock DB
    USER_DB[req.user_id]["status"] = "ACTIVE"
    USER_DB[req.user_id]["failed_attempts"] = 0
    
    return {"message": f"SUCCESS: PeopleSoft account for {req.user_id} unlocked.", "new_status": "ACTIVE"}

@app.post("/api/peoplesoft/reset_password")
def reset_password(req: ResetRequest):
    if req.user_id not in USER_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mock password update
    USER_DB[req.user_id]["password"] = "TempPwd123!"
    
    return {"message": f"SUCCESS: PeopleSoft password for {req.user_id} reset to temporary.", "new_status": "ACTIVE_TEMP_PWD"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
