import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64

st.set_page_config(page_title="History Logs", page_icon="📜", layout="wide")
st.title("📜 Action & Version History")

# Date range picker
today = datetime.now()
start_date = today - timedelta(days=7)
date_range = st.date_input("Select Audit Log Range", [start_date, today])

# Mock history data timeline
history_events = pd.DataFrame({
    "Timestamp": ["2026-09-28 14:22:01", "2026-09-27 09:15:44", "2026-09-25 18:02:11"],
    "User": ["admin@company.com", "system_bot", "dev_team_lead"],
    "Action": ["Updated status of BUG-102 to 'Open'", "Triggered auto-backup", "Resolved Alert: High Memory Usage"]
})

st.table(history_events)






