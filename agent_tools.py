import requests
from langchain_core.tools import tool

# Mock Tools to call FastAPI
FASTAPI_URL = "http://localhost:8000"

@tool
def unlock_peoplesoft_account(user_id: str) -> str:
    """Unlocks a PeopleSoft account for a given user_id after failed login attempts."""
    try:
        response = requests.post(f"{FASTAPI_URL}/api/peoplesoft/unlock", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("message", f"SUCCESS: unlocked {user_id}")
        return f"FAILED: API returned {response.status_code} - {response.text}"
    except Exception as e:
        return f"FAILED to call API: {str(e)}"

@tool
def reset_peoplesoft_pwd(user_id: str) -> str:
    """Resets the PeopleSoft password to a temporary password for a given user_id."""
    try:
        response = requests.post(f"{FASTAPI_URL}/api/peoplesoft/reset_password", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("message", f"SUCCESS: reset {user_id}")
        return f"FAILED: API returned {response.status_code} - {response.text}"
    except Exception as e:
        return f"FAILED to call API: {str(e)}"
