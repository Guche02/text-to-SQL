import streamlit as st
import pandas as pd
import json
import time
from pipeline_1 import chain, intermediate_results
from pipeline_2 import chain2, intermediate_results2
from tools.database_tools import serialize
from httpx import HTTPStatusError

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("SQL Query Generator")
st.markdown("### Chat with SQL Generator")

# Dropdown for choosing between modify or read database
action_type = st.selectbox("Select action", ["Read Database", "Modify Database"])

# Question input for "Read Database"
question = st.text_input("Enter your question:", "")

if action_type == "Modify Database":
    csv_file = st.file_uploader("Upload a CSV file for modification:", type="csv")

parsed_sql_query = "N/A"
raw_db_result = {}
column_names = []
insights = "N/A"
response = ""

def invoke_chain_with_retry(question, max_retries=3, delay=5):
    """Retries invoking the chain if rate limited."""
    attempts = 0
    while attempts < max_retries:
        try:
            return chain.invoke({"question": question})
        except HTTPStatusError as e:
            if e.response.status_code == 429:  
                st.warning("Rate limit exceeded. Retrying in 5 seconds...")
                time.sleep(delay)
                attempts += 1
            else:
                raise e  
    st.error("Failed after multiple attempts due to rate limits.")
    return None

def invoke_chain2_with_retry(query, csv_data, max_retries=3, delay=5):
    """Retries invoking chain2 if rate limited and processes the query with CSV data."""
    attempts = 0
    while attempts < max_retries:
        try:
            if csv_data:
                csv_content = pd.read_csv(csv_data)
            else:
                csv_content = pd.DataFrame()  
            st.success(csv_content)
            result = chain2.invoke({"question": query, "data": csv_content.to_dict(orient="records")})
            return result
        
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                st.warning("Rate limit exceeded. Retrying in 5 seconds...")
                time.sleep(delay)
                attempts += 1
            else:
                raise e  
    st.error("Failed after multiple attempts due to rate limits.")
    return None

if action_type == "Read Database":
    if st.button("Generate Query"):
        if question:
            with st.spinner("Processing..."):
                intermediate_results.clear()
                response = invoke_chain_with_retry(question)

                if response:
                    parsed_sql_query = next(
                        (res["result"] for res in intermediate_results if res["step"] == "AI parsed_sql_query"), "N/A"
                    )
                    raw_db_result = next(
                        (res for res in intermediate_results if res["step"] == "Raw DB Query Result"), {}
                    )
                    column_names = next(
                        (res["result"] for res in intermediate_results if res["step"] == "columns"), []
                    )
                    insights = next(
                        (res["result"] for res in intermediate_results if res["step"] == "final_result"), "N/A"
                    )

                    st.session_state.chat_history.append({
                        "question": question,
                        "parsed_sql_query": parsed_sql_query,
                        "raw_db_result": json.loads(json.dumps(raw_db_result.get("result", "N/A"), default=serialize)),
                        "response": response
                    })

                    st.markdown(f"**Question:** {question}")
                    st.markdown("### Generated SQL Query:")
                    st.code(parsed_sql_query, language="sql")

if action_type == "Modify Database":
    if st.button("Generate Query"):
        if question:  
            with st.spinner("Processing modification..."):
                response = invoke_chain2_with_retry(question, csv_file)

                if response:
                    parsed_sql_query = next(
                        (res["result"] for res in intermediate_results2 if res["step"] == "AI parsed_sql_query"), "N/A"
                    )
                    raw_db_result = next(
                        (res for res in intermediate_results2 if res["step"] == "Raw DB Query Result"), {}
                    )
                    column_names = next(
                        (res["result"] for res in intermediate_results2 if res["step"] == "columns"), []
                    )
                    insights = next(
                        (res["result"] for res in intermediate_results2 if res["step"] == "final_result"), "N/A"
                    )

                    st.session_state.chat_history.append({
                        "question": question,
                        "parsed_sql_query": parsed_sql_query,
                        "raw_db_result": json.loads(json.dumps(raw_db_result.get("result", "N/A"), default=serialize)),
                        "response": response
                    })

                    st.markdown(f"**Question:** {question}")
                    st.markdown("### Generated SQL Query:")
                    st.code(parsed_sql_query, language="sql")

                    if raw_db_result.get("result") == "Query executed successfully.":
                          st.success(raw_db_result["result"])


if isinstance(raw_db_result, dict) and "result" in raw_db_result:
    raw_db_result_list = raw_db_result["result"]

    if isinstance(raw_db_result_list, list) and len(raw_db_result_list) > 1:
        column_names = list(raw_db_result_list[0])  
        data_rows = raw_db_result_list[1:]  

        df = pd.DataFrame(data_rows, columns=column_names)
        top_5_rows = df.head(5)  

        st.markdown("### Tabulated Raw Database Results (Top 5 Rows):")
        st.dataframe(top_5_rows)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Raw DB Results as CSV",
            data=csv_data,
            file_name="raw_db_results.csv",
            mime="text/csv"
        )
    else:
        if raw_db_result.get("result") == "Query executed successfully.":
            st.success(raw_db_result["result"])
        else:
            st.warning("Raw database results are not structured for table/CSV download.")
            
    st.markdown("### Insights:")
    st.write(response)
else:
    st.warning("Please enter a question.")

with st.sidebar:
    st.markdown("## Chat History")
    if st.session_state.chat_history:
        chat_history_json = json.dumps(st.session_state.chat_history, indent=4)
        st.download_button(
            label="📥 Download Chat History",
            data=chat_history_json,
            file_name="chat_history.json",
            mime="application/json"
        )

        for i, entry in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Query {len(st.session_state.chat_history) - i}: {entry['question']}"):
                st.markdown("**SQL Query:**")
                st.code(entry["parsed_sql_query"], language="sql")

                st.markdown("**Raw DB Result (JSON):**")
                st.json(entry["raw_db_result"])  
                
                if isinstance(entry["raw_db_result"], list) and all(isinstance(row, dict) for row in entry["raw_db_result"]):
                    df_history = pd.DataFrame(entry["raw_db_result"])
                    st.markdown("**Tabulated Raw DB Result:**")
                    st.dataframe(df_history)

                st.markdown("**Insights:**")
                st.write(entry["response"])