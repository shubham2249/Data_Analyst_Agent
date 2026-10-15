import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 System Dashboard")

# Mock Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Users", "1,245", "+12%")
col2.metric("Open Bugs", "14", "-4%")
col3.metric("System Uptime", "99.98%")
col4.metric("Alerts (24h)", "3", "+1")

# Mock Chart Data
st.subheader("System Load & Traffic")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['API Gateway', 'Auth Service', 'Database Cluster']
)
st.line_chart(chart_data)
