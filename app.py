import streamlit as st
import time
import uuid
import traceback

from data import get_db
from agent import graph, AgentState
from langgraph.types import Command

# Set Streamlit Page Config
st.set_page_config(page_title="Agentic AMS Dashboard", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for "Techy" But Clean Theme ---
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #f4f7f6;
        color: #2c3e50;
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Remove Global Streamlit Padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2980b9 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(52, 152, 219, 0.2);
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(52, 152, 219, 0.3);
    }
    
    /* Dataframes / Tables */
    .stDataFrame {
        border: 1px solid #e0e6ed;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 2px;
        font-size: 0.85em; /* Reduced size per user request */
    }
    
    /* Logs / Code Blocks */
    .stCodeBlock {
        background-color: #282c34 !important;
        border: 1px solid #e0e6ed !important;
        border-radius: 8px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Info/Warning Boxes */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Column styling trick for depth */
    .dashboard-panel {
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 10px;
        border: 1px solid #e0e6ed;
    }
    
    /* Metrics / Status */
    div[data-testid="stMetricValue"] {
        color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

db = get_db()

# Session State Initialization
if "selected_incident" not in st.session_state:
    st.session_state.selected_incident = None
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = False
if "agent_error" not in st.session_state:
    st.session_state.agent_error = None
if "run_agent_flag" not in st.session_state:
    st.session_state.run_agent_flag = False
if "resume_graph_flag" not in st.session_state:
    st.session_state.resume_graph_flag = False

# --- UI Layout ---
st.title("AIMS (AI-Driven Incident Managed Services)")

if st.session_state.agent_error:
    st.error(f"Agent Execution Error: {st.session_state.agent_error}")

# Create 2 columns: Left (Queue + Details), Right (Agent Console)
col1, col2 = st.columns([0.65, 0.35], gap="small")

with col1:
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.header("Manager View - Incident Queue")
    st.markdown("Current active incidents in the system.")
    
    df = db.get_incidents()
    
    # Custom Row-based Layout
    head_cols = st.columns([1, 2.5, 0.8, 0.8, 1, 1.2, 1.2])
    headers = ["ID", "Description", "Priority", "Status", "Agent", "Created At", "Action"]
    for col, head in zip(head_cols, headers):
        col.markdown(f"**<span style='color:#2980b9;'>{head}</span>**", unsafe_allow_html=True)
        
    st.markdown("<hr style='margin: 0px; border-bottom: 2px solid #e0e6ed;'/>", unsafe_allow_html=True)
    
    for _, row in df.iterrows():
        # Added a minor vertical spacing wrapper for button alignment
        cols = st.columns([1, 2.5, 0.8, 0.8, 1, 1.2, 1.2])
        cols[0].write(row['Incident_ID'])
        cols[1].write(row['Description'])
        
        priority_color = "#e74c3c" if row['Priority'] in ['High', 'Critical'] else "#e67e22" if row['Priority'] == 'Medium' else "#27ae60"
        cols[2].markdown(f"<span style='color:{priority_color}; font-weight:bold;'>{row['Priority']}</span>", unsafe_allow_html=True)
        
        cols[3].write(row['Status'])
        cols[4].write(row['Assigned_Agent'])
        cols[5].write(row['Created_At'])
        
        with cols[6]:
            is_disabled = row['Status'] in ["Resolved", "Escalated"]
            if st.button("Assign to AI Agent", key=f"btn_{row['Incident_ID']}", use_container_width=True, disabled=is_disabled):
                st.session_state.selected_incident = row['Incident_ID']
                st.session_state.run_agent_flag = True
                st.rerun()
                
        st.markdown("<hr style='margin: 5px 0px; border-top: 1px solid #e0e6ed;'/>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_incident:
        st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
        incident_data = db.get_incident(st.session_state.selected_incident)
        st.subheader("Incident Details")
        st.markdown(f"**ID:** {incident_data['Incident_ID']}")
        
        status_color = "green" if incident_data['Status'] == "Resolved" else "red" if incident_data['Status'] == "Escalated" else "black"
        st.markdown(f"**Status:** <span style='color:{status_color}; font-weight:bold;'>{incident_data['Status']}</span>", unsafe_allow_html=True)
        st.markdown(f"**Assignee:** <span style='color:green;'>{incident_data['Assigned_Agent']}</span>", unsafe_allow_html=True)
        st.info(incident_data['Description'])
        
        if st.session_state.awaiting_approval:
            st.warning("⚠️ Human-in-the-Loop Override Required!")
            st.markdown("The agent requested to perform a potential destructive action **(Password Reset)**. Do you approve?")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Approve"):
                    st.session_state.resume_graph_flag = True
                    st.rerun()
            with col_b:
                if st.button("❌ Reject"):
                    db.update_incident(st.session_state.selected_incident, {"Status": "Escalated to L2"})
                    st.session_state.awaiting_approval = False
                    st.session_state.agent_logs.append("⏸️ HUMAN REJECTED: Escalating to L2.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="dashboard-panel" style="min-height: 1px;">', unsafe_allow_html=True)
    st.markdown("### 🤖 Agent Console")
    st.markdown("Observe the AI's internal state and tool executions.")
    console_placeholder = st.empty()
    
    def render_console(logs):
        with console_placeholder.container():
            if logs:
                st.markdown("### 🧠 Thinking Process")
                for log in logs:
                    st.code(log, language="bash")
            else:
                st.info("Agent is idle. Assign an incident to begin.")
                
    render_console(st.session_state.agent_logs)
    st.markdown('</div>', unsafe_allow_html=True)


# --- Background Processing Logic ---

if st.session_state.run_agent_flag:
    st.session_state.run_agent_flag = False
    
    # Reset tracking
    st.session_state.agent_logs = []
    st.session_state.awaiting_approval = False
    st.session_state.agent_error = None
    
    thread_id = str(uuid.uuid4())
    st.session_state.thread_id = thread_id
    cfg = {"configurable": {"thread_id": thread_id}}
    
    incident_data = db.get_incident(st.session_state.selected_incident)
    db.update_incident(st.session_state.selected_incident, {"Status": "Analyzing", "Assigned_Agent": "AI-Gen-1"})
    
    initial_state = AgentState(
        incident_id=incident_data['Incident_ID'],
        incident_details=incident_data['Description'],
        category="",
        current_sop="",
        action_logs=[],
        proposed_tool="",
        is_resolved=False
    )
    
    try:
        stream = graph.stream(initial_state, cfg, stream_mode="values")
        for event in stream:
            if "action_logs" in event and event["action_logs"]:
                st.session_state.agent_logs = event["action_logs"]
                render_console(st.session_state.agent_logs)
            time.sleep(0.5)
            
        final_state = graph.get_state(cfg)
        if final_state and final_state.next:
            st.session_state.awaiting_approval = True
            st.session_state.agent_logs.append("⏸️ GRAPH INTERRUPTED: Awaiting human approval.")
            render_console(st.session_state.agent_logs)
        else:
            is_resolved = final_state.values.get("is_resolved", False) if final_state else False
            if is_resolved:
                db.update_incident(st.session_state.selected_incident, {"Status": "Resolved"})
            else:
                db.update_incident(st.session_state.selected_incident, {"Status": "Escalated"})
                
        # Trigger a rerun at the VERY END to reflect UI changes across the whole page (e.g. data table)
        st.rerun()
        
    except Exception as e:
        st.session_state.agent_error = str(e)
        traceback.print_exc()
        st.rerun()

elif st.session_state.resume_graph_flag:
    st.session_state.resume_graph_flag = False
    st.session_state.awaiting_approval = False
    st.session_state.agent_logs.append("▶️ HUMAN APPROVED: Resuming execution.")
    render_console(st.session_state.agent_logs)
    
    cfg = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    try:
        stream = graph.stream(Command(resume="Approved"), cfg, stream_mode="values")
        for event in stream:
            if "action_logs" in event and event["action_logs"]:
                st.session_state.agent_logs = event["action_logs"]
                render_console(st.session_state.agent_logs)
            time.sleep(0.5)
            
        final_state = graph.get_state(cfg)
        is_resolved = final_state.values.get("is_resolved", False) if final_state else False
        if is_resolved:
            db.update_incident(st.session_state.selected_incident, {"Status": "Resolved"})
        else:
            db.update_incident(st.session_state.selected_incident, {"Status": "Escalated"})
            
        st.rerun()
        
    except Exception as e:
        st.session_state.agent_error = str(e)
        traceback.print_exc()
        st.rerun()
