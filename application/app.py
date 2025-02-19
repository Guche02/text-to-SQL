import streamlit as st
import pandas as pd
import json
from pipeline import chain, intermediate_results
from tools.database_tools import serialize

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("SQL Query Generator")
st.markdown("### Chat with SQL Generator")

question = st.text_input("Enter your question:", "")

# Initialize variables before accessing them
parsed_sql_query = "N/A"
raw_db_result = {}
column_names = []
insights = "N/A"
response = ""

if st.button("Generate Query"):
    if question:
        with st.spinner("Processing..."):
            intermediate_results.clear()
            response = chain.invoke({"question": question})

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

if isinstance(raw_db_result, dict) and "result" in raw_db_result:
    raw_db_result_list = raw_db_result["result"]

    if isinstance(raw_db_result_list, list) and len(raw_db_result_list) > 1:
        column_names = list(raw_db_result_list[0])  
        data_rows = raw_db_result_list[1:]  
        df = pd.DataFrame(data_rows, columns=column_names)

        st.markdown("### Tabulated Raw Database Results:")
        st.dataframe(df)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Raw DB Results as CSV",
            data=csv_data,
            file_name="raw_db_results.csv",
            mime="text/csv"
        )
    else:
        st.warning("Raw database results are not structured for table/CSV download.")
            
    st.markdown("### Insights:")
    st.write(response)

else:
    st.warning("Please enter a question.")

# Sidebar for chat history
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
