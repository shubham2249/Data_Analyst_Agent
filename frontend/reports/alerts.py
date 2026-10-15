import streamlit as st

st.set_page_config(page_title="Alerts", page_icon="🚨", layout="wide")
st.title("🚨 Live System Alerts")

# Interactive alert states
filter_status = st.selectbox("Filter by Severity", ["All", "Critical", "Warning", "Info"])

alerts = [
    {"level": "error", "text": "CRITICAL: Database CPU usage exceeded 95%!", "type": "Critical"},
    {"level": "warning", "text": "WARNING: SSL Certificate expires in 5 days.", "type": "Warning"},
    {"level": "info", "text": "INFO: Scheduled backup completed successfully.", "type": "Info"}
]

for alert in alerts:
    if filter_status == "All" or filter_status == alert["type"]:
        if alert["level"] == "error":
            st.error(alert["text"])
        elif alert["level"] == "warning":
            st.warning(alert["text"])
        else:
            st.info(alert["text"])
