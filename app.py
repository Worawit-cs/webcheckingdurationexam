import streamlit as st
import pandas as pd
from datetime import date, datetime
import extra_streamlit_components as stx
import time

# 1. Config MUST be the very first Streamlit command
st.set_page_config(page_title="CMU Student Scheduler", layout="wide")

# 2. CSS Styles
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=BBH+Sans+Hegarty&family=Titillium+Web:ital,wght@0,200;0,300;0,400;0,600;0,700;0,900;1,200;1,300;1,400;1,600;1,700&display=swap');
        body,[data-testid="stAppViewContainer"],
            section[data-testid="stSidebar"],[data-testid="stHeader"],[data-testid="stBottomBlockContainer"],[data-testid="stSidebar"] {
                # background-image: linear-gradient(135deg,  #41295a 0%, #2F0743 100%);
                font-family: "Titillium Web", sans-serif;
                background-color: #121212; 
            }    
        
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
            margin-top: 2rem;
        }
        .linear-separator {
            border-top: 2px solid #4B0082;
            margin-top: 10px;
            margin-bottom: 10px;
            # color: #4B0082;
        }
        div.stButton > button { 
            font-family: "Titillium Web", sans-serif;
            background-color: #4B0082;
        }
        
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def get_default_data():
    """Returns the default starting row."""
    return pd.DataFrame(
        [
            {
                "DATE": date.today(), 
                "Time": datetime.now().time(),
                "ID Subject": "204111", 
                "Subject": "Fundamentals of Programming"
            }
        ]
    )

def calculate_duration(input_date):
    """Calculates days remaining or passed."""
    if pd.isnull(input_date):
        return "N/A"
    
    # Ensure input is a proper date object
    if isinstance(input_date, datetime):
        input_date = input_date.date()
    
    delta = date.today() - input_date
    days = delta.days
    
    if days == 0:
        return "Today"
    elif days > 0:
        return f"In {days} days"
    else:
        return f"Already pass"

# --- Main Application ---

def main():
    # Title Section
    st.markdown("<h1>Hello CMU STUDENT !!! 🎓</h1>", unsafe_allow_html=True)
    st.markdown("This application is one of the tools that can help you organize your exam schedule more effectively.")
    st.markdown("<hr class='linear-separator'>", unsafe_allow_html=True)
    st.write("<h4>Please type your: Date, ID Subject and your Subject's name. 📋</h4>", unsafe_allow_html=True)

    # --- Cookie Manager Init ---
    cookie_manager = stx.CookieManager()
    
    # Try to get data from cookie
    # Note: On the very first run, this might return None until the component mounts
    cookie_data = cookie_manager.get(cookie="subject_table_data")

    # --- Load Data Logic ---
    if "data" not in st.session_state:
        # If cookie exists, try to load it
        if cookie_data:
            try:
                # 1. Parse JSON string back to DataFrame
                df = pd.read_json(cookie_data)
                
                # 2. Fix Date Columns (JSON makes them strings/timestamps)
                if "DATE" in df.columns:
                    df["DATE"] = pd.to_datetime(df["DATE"]).dt.date
                
                # 3. Fix Time Columns
                if "Time" in df.columns:
                    # Force conversion to string first to handle inconsistent formats
                    df["Time"] = pd.to_datetime(df["Time"].astype(str)).dt.time
                
                st.session_state.data = df
                # Optional: st.toast("Loaded saved data!", icon="🍪")
            except Exception as e:
                st.warning(f"Error loading saved data: {e}")
                st.session_state.data = get_default_data()
        else:
            # No cookie found, load default
            st.session_state.data = get_default_data()

    # --- Table Configuration ---
    column_configuration = {
        "DATE": st.column_config.DateColumn("Date", format="YYYY-MM-DD", required=True),
        "Time": st.column_config.TimeColumn("Time", format="h:mm a", step=60),
        "ID Subject": st.column_config.TextColumn("ID Subject", validate="^[A-Za-z0-9-_]+$", required=True),
        "Subject": st.column_config.TextColumn("Subject Name", width="large", required=True),
    }

    # --- Display Editor ---
    st.info("Click on a cell to edit. Click the '+' row at the bottom to add a new entry.")
    
    edited_df = st.data_editor(
        st.session_state.data,
        column_config=column_configuration,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor"
    )

    # --- Analytics Section ---
    st.divider()
    st.write("### Resulting DataFrame (with Duration) 📝:")

    if not edited_df.empty:
        results_df = edited_df.copy()
        results_df["Duration"] = results_df["DATE"].apply(calculate_duration)
        st.dataframe(results_df)

    # --- Save Logic ---
    if st.button("Save Data"):
        # 1. Convert DataFrame to JSON string
        # We create a copy formatted specifically for JSON storage
        save_df = edited_df.copy()
        
        # Convert date/time objects to simple strings for JSON
        save_df["DATE"] = pd.to_datetime(save_df["DATE"]).dt.strftime('%Y-%m-%d')
        save_df["Time"] = save_df["Time"].astype(str)
        
        json_data = save_df.to_json(orient="records")
        
        # 2. Save to Cookie
        # key="save_handler" helps unique identification
        cookie_manager.set("subject_table_data", json_data)
        
        st.success(f"Saved {len(edited_df)} rows to cookies successfully!")

if __name__ == "__main__":
    main()