import streamlit as st
import json
import os
import requests

st.set_page_config(page_title="Jobs Management Dashboard", page_icon="⚙️", layout="wide")

# --- Custom CSS for beautiful UI ---
st.markdown("""
<style>
    .job-card {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #e0e6ed;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .job-id {
        font-weight: 700;
        color: #2c3e50;
        font-size: 16px;
    }
    .status-badge {
        font-weight: 600;
        padding: 6px 16px;
        border-radius: 20px;
        color: white;
        font-size: 13px;
        text-align: center;
        width: 120px;
        display: inline-block;
    }
    .status-SUCCESSFUL, .status-FINISHED { background-color: #27ae60; }
    .status-FAILED { background-color: #e74c3c; }
    .status-RUNNING { background-color: #007bff; }
    .status-ON_HOLD { background-color: #f39c12; }
    .status-UNKNOWN { background-color: #95a5a6; }
    
    .panel {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
        min-height: 600px;
    }
</style>
""", unsafe_allow_html=True)

# Function to fetch jobs from API (or fallback to JSON)
def get_jobs():
    try:
        # For this mock, we will just read the DB file since the API endpoints 
        # only fetch single jobs status/logs and there is no GET /jobs endpoint.
        if os.path.exists("jobs_db.json"):
            with open("jobs_db.json", "r") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Failed to load jobs data: {e}")
    return {}

st.title("⚙️ Jobs Execution Dashboard")
st.markdown("Monitor system jobs in real-time. Select a job to view its detailed execution logs.")

# Initialize session state for the selected log
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None
if "selected_job_log" not in st.session_state:
    st.session_state.selected_job_log = None

jobs = get_jobs()

# Create two columns (Left for Job List, Right for Log Details)
col1, space, col2 = st.columns([0.55, 0.05, 0.4])

with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 📋 Active Jobs List")
    st.markdown("---")
    
    if not jobs:
        st.info("No jobs found in the database.")
    else:
        for job_id, details in jobs.items():
            status = details.get("status", "UNKNOWN")
            
            # Use columns to align items nicely inside the loop
            c_job, c_status, c_action = st.columns([0.3, 0.4, 0.3], vertical_alignment="center")
            
            with c_job:
                st.markdown(f"<span class='job-id'>🗂️ {job_id}</span>", unsafe_allow_html=True)
            
            with c_status:
                badge_class = f"status-{status}" if status in ["SUCCESSFUL", "FINISHED", "FAILED", "RUNNING", "ON_HOLD"] else "status-UNKNOWN"
                st.markdown(f"<span class='status-badge {badge_class}'>{status}</span>", unsafe_allow_html=True)
                
            with c_action:
                # View Log button
                if st.button("View Log 📄", key=f"btn_{job_id}", use_container_width=True):
                    st.session_state.selected_job_id = job_id
                    st.session_state.selected_job_log = details.get("log", "No log available.")
            
            st.write("") # small spacing
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 📝 Log Viewer")
    st.markdown("---")
    
    if st.session_state.selected_job_id:
        st.markdown(f"**Job ID:** `{st.session_state.selected_job_id}`")
        status_for_selected = jobs.get(st.session_state.selected_job_id, {}).get("status", "")
        if status_for_selected:
            st.markdown(f"**Current Status:** {status_for_selected}")
        
        st.markdown("<br><b>Execution Log:</b>", unsafe_allow_html=True)
        # Using st.info or st.code to display the log nicely
        st.info(st.session_state.selected_job_log)
        
        # Alternatively display as code block
        st.code(st.session_state.selected_job_log, language="text")
    else:
        st.info("⬅️ Click on a 'View Log' button next to a job on the left to display its execution details here.")
        
    st.markdown('</div>', unsafe_allow_html=True)
