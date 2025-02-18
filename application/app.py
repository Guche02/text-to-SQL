import streamlit as st
from tools.pipeline import chain, generate_insights_from_intermediate

intermediate_results = []

st.title("SQL Query Generator")
st.markdown("### Chat with SQL Generator")
question = st.text_input("Enter your question:", "")

if st.button("Generate Query"):
    if question:
        with st.spinner("Processing..."):
            response = chain.invoke({"question": question})
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Generated Results:** {response}")
            
    else:
        st.warning("Please enter a question.")
