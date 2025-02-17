import streamlit as st
from tools.pipeline import chain  # Importing your LangChain pipeline

st.title("SQL Query Generator")

question = st.text_input("Enter your question:", "")

if st.button("Generate Query"):
    if question:
        with st.spinner("Processing..."):
            response = chain.invoke({"question": question})
            st.write("### Generated Response:")
            st.json(response)
    else:
        st.warning("Please enter a question.")

