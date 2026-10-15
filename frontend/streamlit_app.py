import io
import os

import pandas as pd
import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "INSIGHTIQ_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

ANALYZE_URL = f"{API_BASE_URL}/api/analyze-question"

st.set_page_config(
    page_title="InsightIQ | AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 InsightIQ")
st.caption("An AI-powered data analyst that turns questions into reproducible analysis.")

st.sidebar.header("About InsightIQ")
st.sidebar.write(
    "Upload a dataset, ask a question in plain English, "
    "and inspect the analysis plan and results."
)
st.sidebar.caption(f"Backend: {API_BASE_URL}")

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv"],
    help="The first version supports CSV files.",
)

if uploaded_file is None:
    st.info("Upload a CSV file to get started.")
    st.stop()

file_bytes = uploaded_file.getvalue()

try:
    dataframe = pd.read_csv(io.BytesIO(file_bytes))
except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
    st.error(f"Could not read this CSV file: {exc}")
    st.stop()

if dataframe.empty or len(dataframe.columns) == 0:
    st.error("The uploaded CSV does not contain usable tabular data.")
    st.stop()

st.subheader("Dataset overview")

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Rows", f"{len(dataframe):,}")
metric2.metric("Columns", f"{len(dataframe.columns):,}")
metric3.metric(
    "Missing values",
    f"{int(dataframe.isna().sum().sum()):,}",
)

with st.expander("Preview dataset", expanded=True):
    st.dataframe(dataframe.head(100), use_container_width=True)

with st.expander("Column information"):
    column_info = pd.DataFrame(
        {
            "Column": dataframe.columns.astype(str),
            "Data type": dataframe.dtypes.astype(str).values,
            "Missing values": dataframe.isna().sum().values,
        }
    )
    st.dataframe(column_info, use_container_width=True)

st.divider()
st.subheader("Ask your data")

question = st.text_area(
    "What would you like to investigate?",
    placeholder=(
        "Example: Calculate average revenue by region "
        "and identify the highest-performing region."
    ),
    max_chars=2000,
    height=100,
)

analyze_clicked = st.button(
    "Analyze dataset",
    type="primary",
    disabled=not question.strip(),
)

if analyze_clicked:
    with st.spinner("Planning and executing your analysis..."):
        try:
            response = requests.post(
                ANALYZE_URL,
                files={
                    "file": (
                        uploaded_file.name,
                        file_bytes,
                        "text/csv",
                    )
                },
                data={"question": question.strip()},
                timeout=(5, 120),
            )

            if not response.ok:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text

                st.error(
                    f"Analysis failed (HTTP {response.status_code}): {detail}"
                )
                st.stop()

            result = response.json()

        except requests.Timeout:
            st.error(
                "The analysis request timed out. Check the backend logs "
                "and try again."
            )
            st.stop()
        except requests.ConnectionError:
            st.error(
                "Could not connect to FastAPI. Start the backend and try again."
            )
            st.stop()
        except requests.RequestException as exc:
            st.error(f"Request failed: {exc}")
            st.stop()
        except ValueError:
            st.error("The backend returned an invalid JSON response.")
            st.stop()

    st.session_state["analysis_result"] = result
    st.session_state["analysis_question"] = question.strip()

result = st.session_state.get("analysis_result")

if result:
    st.divider()
    st.subheader("Analysis report")

    st.write("**Question:**", result.get("question", ""))
    st.write("**Goal:**", result.get("goal", ""))

    status = result.get("status", "unknown")
    if status == "completed":
        st.success("Analysis completed.")
    else:
        st.warning("Analysis did not complete successfully.")

    plan = result.get("plan")
    if plan:
        with st.expander("View generated analysis plan"):
            st.json(plan)

    st.subheader("Execution steps")

    steps = result.get("steps", [])
    if not steps:
        st.info("The backend returned no execution steps.")

    for index, step in enumerate(steps, start=1):
        step_status = step.get("status", "unknown")
        title = (
            f"{index}. {step.get('tool_name', 'Unknown tool')} "
            f"— {step_status}"
        )

        with st.expander(title):
            st.write("**Step ID:**", step.get("step_id", ""))
            if step.get("error"):
                st.error(step["error"])

            output = step.get("output")
            if output is not None:
                st.json(output)

    st.subheader("Final result")

    final_result = result.get("final_result")

    if isinstance(final_result, dict) and isinstance(
        final_result.get("data"), list
    ):
        result_df = pd.DataFrame(final_result["data"])

        if not result_df.empty:
            st.dataframe(result_df, use_container_width=True)
        else:
            st.info("The analysis returned an empty table.")

        csv_bytes = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download results as CSV",
            data=csv_bytes,
            file_name="insightiq_results.csv",
            mime="text/csv",
        )

        metadata = final_result.get("metadata")
        if metadata:
            with st.expander("Result metadata"):
                st.json(metadata)
    elif final_result is not None:
        st.json(final_result)
    else:
        st.info("No final result was returned.")

    with st.expander("Working dataset"):
        working_dataset = result.get("working_dataset", {})
        working_data = working_dataset.get("data", [])

        if working_data:
            st.dataframe(
                pd.DataFrame(working_data),
                use_container_width=True,
            )
        else:
            st.info("No working dataset preview is available.")