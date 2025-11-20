import streamlit as st
import pandas as pd
from datetime import date, datetime
import extra_streamlit_components as stx
import time
import os
from pathlib import Path

# /home/worawit/Documents/allProject/realProject/webcheckingdurationexam/image/cs_cmu.png
# PATH_CS_LOGO = Path.home()/"webcheckingdurationexam" / "image" /"cs_cmu.png"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATH_CS_LOGO = os.path.join(PROJECT_ROOT,"webcheckingdurationexam/image/cs_cmu.png")
print(PROJECT_ROOT)
# 1. Config MUST be the very first Streamlit command
st.set_page_config(page_title="CMU Student Scheduler", layout="wide")

# 2. CSS Styles
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=BBH+Sans+Hegarty&family=Titillium+Web:ital,wght@0,200;0,300;0,400;0,600;0,700;0,900;1,200;1,300;1,400;1,600;1,700&display=swap');
        body,[data-testid="stAppViewContainer"],
            section[data-testid="stSidebar"],[data-testid="stHeader"],[data-testid="stBottomBlockContainer"],[data-testid="stSidebar"] {
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
        }
        div.stButton > button { 
            font-family: "Titillium Web", sans-serif;
            background-color: #4B0082;
        }
        section[data-testid="stSidebar"] h1{
            font-size: 40px;
            margin-bottom: 0.5rem;
            padding: 0 0;
        }
        section[data-testid="stSidebar"] h2{
            font-size: 30px;
            padding: 0 0;
        }
         section[data-testid="stSidebar"] {
            width: 500px; 
            !important; 
            # gap: 0.1rem;
            # margin: 0,0;
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
    
    delta = input_date - date.today()
    days = delta.days
    
    month = days//30
    remain_day = days-(month*30)
    
    result = f"In {month} months and {remain_day} days" if month != 0 else f"In {days} days"

    # Checking formatting output
    if month == 1:
        result = result.replace("months","month")
    elif days == 1:
        result = result.replace("days","days")

    if days == 0:
        return "Today"
    elif days > 0:
        return result
    else:
        return f"Already pass"

# --- Main Application ---

def main():
    # Title Section
    st.markdown("<h1>Hello CMU STUDENT !!! 🎓</h1>", unsafe_allow_html=True)
    st.markdown("This application is one of the tools that can help you organize your exam schedule more effectively.")
    st.markdown("<hr class='linear-separator'>", unsafe_allow_html=True)
    st.write("<h4>Please type your: Date, ID Subject and your Subject's name. 📋</h4>", unsafe_allow_html=True)

    with st.sidebar:
        global PATH_CS_LOGO
        col1,col2 = st.columns([3,1])
        with col1:
            st.title("About")
        with col2:
            st.title("ℹ️")
        st.markdown("<hr class='linear-separator'>", unsafe_allow_html=True)
        st.markdown("<h2>1. Project Background</h2>",unsafe_allow_html=True)
        st.markdown("- This project originated from my laziness to manually calculate the number of days left until exam day. At first, I created a simple Python script for myself, but after my friends and my girlfriend wanted to use it as well, I decided to build this website.")
        st.markdown("<h2>2. Recommendation</h2>",unsafe_allow_html=True)
        st.markdown("- If the text appears too dark and difficult to read, go to the three-dot menu → Settings → Choose app theme.")
        st.markdown("- When you press the reset button, if nothing changes, please refresh the webpage and try again.")
        st.markdown("<hr class='linear-separator'>", unsafe_allow_html=True)
        st.markdown("<h1>Created by a Computer Science student at Chiang Mai University.</h1>", unsafe_allow_html=True)
        col1,col2,col3 = st.columns([1,3,1])
        with col2:
            st.image(PATH_CS_LOGO,width=200)
    # --- Cookie Manager Init ---
    cookie_manager = stx.CookieManager()
    
    # Try to get data from cookie
    cookie_data = cookie_manager.get(cookie="subject_table_data")

    # --- Load Data Logic (FIXED) ---
    
    # 1. Setup Default state if not exists
    if "data" not in st.session_state:
        st.session_state.data = get_default_data()
        st.session_state.is_default = True # Mark as default

    # 2. Handle Cookie Loading (Race Condition Fix)
    # If we have cookie data AND we are currently showing default data -> Load the cookie!
    if cookie_data and st.session_state.get("is_default", False):
        try:
            # A. Handle Format (List vs JSON String)
            if isinstance(cookie_data, list):
                df = pd.DataFrame(cookie_data)
            elif isinstance(cookie_data, str):
                df = pd.read_json(cookie_data)
            else:
                df = get_default_data()

            # B. Fix Date Columns (Handle NaT/None)
            if "DATE" in df.columns:
                df["DATE"] = pd.to_datetime(df["DATE"], errors='coerce').dt.date
            
            # C. Fix Time Columns (CRITICAL FIX for StreamlitAPIException)
            if "Time" in df.columns:
                # Convert to string first -> then to datetime -> then extract time
                # errors='coerce' turns bad data into NaT instead of crashing
                df["Time"] = pd.to_datetime(df["Time"].astype(str), errors='coerce').dt.time
            
            # D. Clean Bad Data (Drop rows with missing dates)
            df = df.dropna(subset=['DATE'])
            df = df.reset_index(drop=True)

            # Update Session State
            st.session_state.data = df
            st.session_state.is_default = False # It's real data now
            
            st.rerun() # Force reload to show new data immediately

        except Exception as e:
            st.warning(f"Error loading saved data: {e}")
            # If data is corrupt, clear cookie to prevent loop
            # cookie_manager.delete("subject_table_data") 

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
        # Check if Duration calculation fails
        try:
            results_df["Duration"] = results_df["DATE"].apply(calculate_duration)
            st.dataframe(results_df)
        except Exception as e:
            st.error("Error calculating duration. Please check date formats.")

    # --- Action Buttons (Save & Clear) ---
    st.markdown("<br>", unsafe_allow_html=True) # เว้นบรรทัดนิดนึง
    col1, col2 = st.columns([1, 4]) # แบ่งคอลัมน์: ปุ่ม Save เล็กหน่อย, ปุ่ม Clear อยู่ขวา หรือจัดตามชอบ

    with col1:
        if st.button("💾 Save Data", use_container_width=True):
            # 1. Update Session State
            st.session_state.data = edited_df
            st.session_state.is_default = False

            # 2. Prepare for JSON
            save_df = edited_df.copy()
            save_df["DATE"] = pd.to_datetime(save_df["DATE"]).dt.strftime('%Y-%m-%d')
            save_df["Time"] = save_df["Time"].astype(str)
            
            # 3. Save to Cookie
            json_data = save_df.to_json(orient="records")
            cookie_manager.set("subject_table_data", json_data)
            
            st.toast("Data saved successfully!", icon="💾")
            time.sleep(0.5)

    with col2:
        if st.button("🗑️ Reset / Clear All", type="primary"):
            # 1. ลบ Cookie
            cookie_manager.delete("subject_table_data")
            
            # 2. รีเซ็ตข้อมูล
            st.session_state.data = get_default_data()
            st.session_state.is_default = True
            
            # 3. [เพิ่มตรงนี้] สร้าง Flag บอกว่าเพิ่งลบไป
            st.session_state.just_deleted = True 
            
            st.toast("All data cleared!", icon="🗑️")
            time.sleep(0.5)
            st.rerun()

if __name__ == "__main__":
    main()