import os
import requests
from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Define the Agent State
class AgentState(TypedDict):
    incident_id: str
    incident_details: str
    category: str
    current_sop: str
    action_logs: List[str]
    proposed_tool: str
    is_resolved: bool

# Initialize LLM
# Using Gemini 2.5 Flash as standard alias, if Gemini 3 Flash specifically requested by environment it can be adjusted
# For now, we use the standard identifier that is likely available in the SDK.
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


# Mock Tools to call FastAPI
FASTAPI_URL = "http://localhost:8000"

def mock_peoplesoft_api_unlock_account(user_id: str) -> str:
    try:
        response = requests.post(f"{FASTAPI_URL}/api/peoplesoft/unlock", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("message", f"SUCCESS: unlocked {user_id}")
        return f"FAILED: API returned {response.status_code} - {response.text}"
    except Exception as e:
        return f"FAILED to call API: {str(e)}"

def mock_peoplesoft_api_reset_password(user_id: str) -> str:
    try:
        response = requests.post(f"{FASTAPI_URL}/api/peoplesoft/reset_password", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("message", f"SUCCESS: reset {user_id}")
        return f"FAILED: API returned {response.status_code} - {response.text}"
    except Exception as e:
        return f"FAILED to call API: {str(e)}"

# Nodes
def classify_incident(state: AgentState):
    log = f"Node [Classification]: Classifying incident based on description."
    incident_details = state.get("incident_details", "")
    
    prompt = f"""
    Classify the following incident description into one of three categories:
    1. 'Account_Unlock' - if the user is locked out after failed attempts.
    2. 'Password_Reset' - if the user forgot their password and needs a reset.
    3. 'Other' - anything else (performance, bug, general access).
    
    Incident Description: {incident_details}
    
    Respond ONLY with the category name exactly as defined above.
    """
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    category = response.content.strip()
    print(category)
    
    return {
        "category": category, 
        "action_logs": state.get("action_logs", []) + [log, f"Classification Result: {category}"]
    }

def retrieve_sop(state: AgentState):
    log = f"Node [SOP Retriever]: Retrieving SOP based on category."
    category = state.get("category", "")
    
    sop_content = "No SOP specific to this issue. Escalating to human."
    sop_filename = "N/A"
    
    working_dir = os.path.dirname(os.path.abspath(__file__))
    
    if category == "Account_Unlock":
        sop_filename = "SOP_Account_Unlock_PeopleSoft.txt"
    elif category == "Password_Reset":
        sop_filename = "SOP_Password_Reset_PeopleSoft.txt"
        
    if sop_filename != "N/A":
        sop_path = os.path.join(working_dir, sop_filename)
        if os.path.exists(sop_path):
            with open(sop_path, "r", encoding="utf-8") as f:
                sop_content = f.read()
        else:
            sop_content = f"Error: Could not find {sop_filename}"
            
    return {
        "current_sop": sop_content,
        "action_logs": state.get("action_logs", []) + [log, f"Read SOP: {sop_filename}"]
    }

def determine_action(state: AgentState):
    log = f"Node [Action Node]: Determining tool based on SOP."
    category = state.get("category", "")
    
    proposed_tool = "None"
    
    if category == "Account_Unlock":
        proposed_tool = "unlock_peoplesoft_account"
    elif category == "Password_Reset":
        proposed_tool = "reset_peoplesoft_pwd"
        
    return {
        "proposed_tool": proposed_tool,
        "action_logs": state.get("action_logs", []) + [log, f"Identified Required Tool: {proposed_tool}"]
    }

def human_approval_check(state: AgentState):
    """Router to determine if we need human approval before execution"""
    proposed_tool = state.get("proposed_tool", "")
    if proposed_tool == "reset_peoplesoft_pwd":
        return "human_approval"
    return "execute_action"

def execute_action(state: AgentState):
    log = f"Node [Execution Sim]: Executing action."
    proposed_tool = state.get("proposed_tool", "")
    incident_details = state.get("incident_details", "")
    
    # Very basic naive extraction of user id for mock execution
    # In a real app the LLM would extract this in the determine_action node
    user_id = "user"
    if "jdoe" in incident_details.lower(): user_id = "jdoe"
    elif "msmith" in incident_details.lower(): user_id = "msmith"
    
    result = "No Action Taken and Escalated."
    is_resolved = False
    
    if proposed_tool == "unlock_peoplesoft_account":
        result = mock_peoplesoft_api_unlock_account(user_id)
        is_resolved = True
    elif proposed_tool == "reset_peoplesoft_pwd":
        result = mock_peoplesoft_api_reset_password(user_id)
        is_resolved = True
        
    return {
        "is_resolved": is_resolved,
        "action_logs": state.get("action_logs", []) + [log, f"Tool Result: {result}"]
    }

# Build the Graph
builder = StateGraph(AgentState)

#builder.set_entry_point("classify")

builder.add_node("classify_incident", classify_incident)
builder.add_node("retrieve_sop", retrieve_sop)
builder.add_node("determine_action", determine_action)
builder.add_node("execute_action", execute_action)

# For human-in-the-loop we simply create a dummy node.
# LangGraph interrupts BEFORE this node executes.
def human_approval_node(state: AgentState):
    pass # Just a placeholder

builder.add_node("human_approval_node", human_approval_node)

builder.add_edge(START, "classify_incident")
builder.add_edge("classify_incident", "retrieve_sop")
builder.add_edge("retrieve_sop", "determine_action")

# Conditional routing based on the tool
builder.add_conditional_edges(
    "determine_action",
    human_approval_check,
    {
        "human_approval": "human_approval_node",
        "execute_action": "execute_action"
    }
)

builder.add_edge("human_approval_node", "execute_action")
builder.add_edge("execute_action", END)

# Compile with interrupt
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["human_approval_node"])
