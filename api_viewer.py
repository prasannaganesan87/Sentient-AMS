import streamlit as st
import requests
import textwrap
import pandas as pd

# --- Custom CSS for beautiful UI ---
st.markdown("""
<style>
    .user-card {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 24px;
        margin-top: 20px;
        border: 1px solid #e0e6ed;
    }
    .user-header {
        color: #2c3e50;
        margin-top: 0;
        font-size: 24px;
        font-weight: 700;
        border-bottom: 2px solid #f4f7f6;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
    .status-badge {
        font-weight: bold;
        padding: 6px 12px;
        border-radius: 20px;
        color: white;
        display: inline-block;
        font-size: 14px;
    }
    .status-active { background-color: #27ae60; }
    .status-locked { background-color: #e74c3c; }
    .status-unknown { background-color: #95a5a6; }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f4f7f6;
        font-size: 16px;
        color: #34495e;
    }
    .detail-row:last-child {
        border-bottom: none;
    }
    .detail-label {
        font-weight: 600;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 API User Lookup")
st.markdown("Enter a User ID to view their details from the FastAPI Backend.")

# Search Input
col1, col2 = st.columns([0.8, 0.2], vertical_alignment="bottom")
with col1:
    user_id_input = st.text_input("User ID (e.g., jdoe, msmith, user):", value="jdoe")
with col2:
    search_clicked = st.button("Search", use_container_width=True)

if search_clicked or user_id_input:
    if user_id_input.strip() == "":
        st.warning("Please enter a valid User ID.")
    else:
        with st.spinner(f"Fetching data for {user_id_input}..."):
            try:
                # Call the FastAPI backend
                response = requests.get(f"http://localhost:8000/users/{user_id_input.strip()}", timeout=5)
                
                if response.status_code == 200:
                    user_data = response.json()
                    
                    # Status styling
                    status = user_data.get('status', 'UNKNOWN')
                    if status == 'ACTIVE':
                        badge_class = "status-active"
                    elif status == 'LOCKED':
                        badge_class = "status-locked"
                    else:
                        badge_class = "status-unknown"
                        
                    
                    st.markdown("### 👤 User Profile Summary")
                    
                    # Top Metrics
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("User ID", user_data.get('user_id', user_id_input))
                    with col_m2:
                        st.metric("Status", status)
                    with col_m3:
                        st.metric("Failed Attempts", user_data.get('failed_attempts', 'N/A'))
                        
                    st.divider()
                    
                    st.markdown("### 📋 Detailed User Record")
                    # Convert single dict to DataFrame for tabular display
                    df = pd.DataFrame([user_data])
                    
                    # Highlight status row in the table
                    def highlight_status(val):
                        if val == 'LOCKED':
                            return 'background-color: #ffeaea; color: #d32f2f; font-weight: bold;'
                        elif val == 'ACTIVE':
                            return 'background-color: #eaffea; color: #2e7d32; font-weight: bold;'
                        return ''
                    
                    try:
                        styled_df = df.style.map(highlight_status, subset=['status'])
                    except AttributeError:
                        styled_df = df.style.applymap(highlight_status, subset=['status'])
                        
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    st.success("Successfully retrieved user from API!")
                    
                elif response.status_code == 404:
                    st.error(f"User '{user_id_input}' not found in the database.")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 **Connection Error:** Could not connect to the API. Is FastAPI running on `http://localhost:8000`? Run `python fastapi_app.py` first.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
