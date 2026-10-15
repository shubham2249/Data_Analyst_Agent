import streamlit as st

st.set_page_config(page_title="Global Search", page_icon="🔍", layout="wide")
st.title("🔍 Global Search")

search_query = st.text_input("Search for alerts, bugs, user IDs, or logs...", placeholder="e.g., BUG-101")

if search_query:
    st.write(f"Showing results for: **{search_query}**")
    
    # Simple mockup match response
    st.info("💡 Found 1 matching item in **Bugs**")
    st.json({
        "Item ID": search_query,
        "Type": "Bug Ticket",
        "Assigned To": "Jane Doe",
        "Last Updated": "2 hours ago"
    })
else:
    st.caption("Enter a query above to scan the environment database.")
