import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bug Tracker", page_icon="🪲", layout="wide")
st.title("Bug Tracking System")

# Simple form to file a bug
with st.expander("Report a New Bug"):
    with st.form("bug_form"):
        title = st.text_input("Bug Title")
        severity = st.select_slider("Severity", options=["Low", "Medium", "High", "Blocker"])
        description = st.text_area("Steps to Reproduce")
        submitted = st.form_submit_button("Submit Bug")
        
        if submitted:
            st.success(f"Bug '{title}' submitted successfully!")

# Mock existing bugs table
st.subheader("Active Bug Backlog")
bug_data = pd.DataFrame({
    "ID": ["BUG-101", "BUG-102", "BUG-103"],
    "Title": ["Login button broken on mobile", "Checkout page timeout", "Typo in footer"],
    "Severity": ["High", "Blocker", "Low"],
    "Status": ["In Progress", "Open", "Resolved"]
})
st.dataframe(bug_data, use_container_width=True)
