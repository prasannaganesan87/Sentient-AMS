import pandas as pd
from datetime import datetime

# In-memory mock data
INITIAL_INCIDENTS = [
    {
        "Incident_ID": "INC-1001",
        "Description": "User robert19 is locked out of PeopleSoft after multiple failed login attempts.",
        "Priority": "High",
        "Status": "New",
        "Assigned_Agent": "Unassigned",
        "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "Incident_ID": "INC-1002",
        "Description": "User msmith2 forgot their PeopleSoft password and needs a reset.",
        "Priority": "Medium",
        "Status": "New",
        "Assigned_Agent": "Unassigned",
        "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "Incident_ID": "INC-1003",
        "Description": "The main dashboard is loading very slowly for the finance region.",
        "Priority": "High",
        "Status": "New",
        "Assigned_Agent": "Unassigned",
        "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "Incident_ID": "INC-1004",
        "Description": "Getting a 500 internal server error when trying to generate the monthly report in the HR module.",
        "Priority": "Critical",
        "Status": "New",
        "Assigned_Agent": "Unassigned",
        "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "Incident_ID": "INC-1005",
        "Description": "Please post complete the ETL job JOB-002 so it can be retriggered.",
        "Priority": "High",
        "Status": "New",
        "Assigned_Agent": "Unassigned",
        "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

class IncidentDatabase:
    def __init__(self):
        self.df = pd.DataFrame(INITIAL_INCIDENTS)

    def get_incidents(self) -> pd.DataFrame:
        return self.df

    def get_incident(self, incident_id: str) -> dict:
        incident = self.df[self.df['Incident_ID'] == incident_id]
        if not incident.empty:
            return incident.iloc[0].to_dict()
        return None

    def update_incident(self, incident_id: str, updates: dict):
        for key, value in updates.items():
            self.df.loc[self.df['Incident_ID'] == incident_id, key] = value

    def reset_db(self):
        self.df = pd.DataFrame(INITIAL_INCIDENTS)

# Global singleton for the session (Streamlit handles actual caching/session state)
db_instance = IncidentDatabase()

def get_db() -> IncidentDatabase:
    return db_instance
