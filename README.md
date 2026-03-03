# Sentient-AMS (AI-Driven Incident Managed Services)

A prototype system demonstrating an AI agentic workflow for an IT Incident Management dashboard. This application showcases how an AI agent can read tickets from a queue, classify them, retrieve Standard Operating Procedures (SOPs), and take automated or human-approved actions to resolve incidents.

## Features

- **Manager Dashboard**: A Streamlit-based UI to view the incident queue, assign tickets to the AI agent, and monitor progress.
- **Agentic Workflow**: Built with [LangGraph](https://python.langchain.com/docs/langgraph/) and LangChain, utilizing Google's Gemini models to process and resolve incidents.
- **Human-in-the-Loop (HITL)**: Sensitive actions (like resetting a password) trigger a pause in the agent's workflow, requiring explicit human approval on the dashboard before execution.
- **Mock FastAPI Backend**: Simulates an enterprise PeopleSoft environment with API endpoints for unlocking accounts and resetting passwords.
- **Agent Tools Module**: Extensible tool execution isolated in `agent_tools.py` for clear separation of concerns.

## Tech Stack

- **Frontend:** Streamlit
- **Backend/API:** FastAPI, Uvicorn
- **AI/LLM:** LangChain, LangGraph, Google Gemini (`gemini-2.5-flash`)
- **Data/State:** Pandas (for mock incident DB), LangGraph `MemorySaver`

## Prerequisites

Ensure you have Python 3.8+ installed. You also need a Google Gemini API Key.

1. Clone the repository.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Google API key in a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the Application

This system consists of two separate applications that need to be run concurrently: the mock API server and the Streamlit dashboard.

### 1. Start the Mock FastAPI Server

This server simulates the PeopleSoft backend.

```bash
python fastapi_app.py
```
*(Runs on `http://localhost:8000` by default)*

### 2. Start the Streamlit Dashboard

In a new terminal, run the main manager dashboard.

```bash
streamlit run app.py
```

## How It Works

1. **Queue View**: The Streamlit app reads from a mock Pandas database (`data.py`) containing pending IT incidents.
2. **Assignment**: A manager selects an incident and clicks "Assign to AI Agent".
3. **Agent State Graph** (`agent.py`):
   - **Classify**: The LLM reads the incident description and categorizes it (e.g., Account_Unlock, Password_Reset, Other).
   - **Retrieve SOP**: Based on the category, the agent reads the corresponding SOP text file from the local `SOP/` directory.
   - **Determine Action**: The LLM decides which tool needs to be executed based on the SOP (from `agent_tools.py`).
   - **Human Approval Check**: LangGraph interrupts the workflow if the selected tool is high-risk (like a password reset), waiting for manager approval via the Streamlit UI.
   - **Execute**: The tool calls the local FastAPI application to resolve the issue.

## Project Structure

- `app.py`: Main Streamlit dashboard application.
- `agent.py`: LangGraph state machine definition and nodes.
- `agent_tools.py`: LangChain tools definition (API calls to FastAPI).
- `data.py`: Mock incident database using Pandas.
- `fastapi_app.py`: Mock PeopleSoft server.
- `SOP/`: Directory containing textual SOP instructions.