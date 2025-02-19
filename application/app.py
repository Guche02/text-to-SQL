import streamlit as st
from pipeline import chain

# st.set_option('server.fileWatcherType', 'none')

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