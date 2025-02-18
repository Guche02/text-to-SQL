from langchain.prompts import PromptTemplate


sql_gen_prompt_template = PromptTemplate(
    template="""
    You are an expert SQL Generator. Based on the provided database schema information, generate only One syntactically correct SQL query to answer the following question. Ensure that your query uses only the relevant tables and columns based on the schema information provided. The query should be limited to at most 1 results unless the question specifies a different number.

    Schema Information:
    {schema_info}

    Question:
    {question}

    SQL Query:
    """,
    input_variables=["schema_info", "question"]
)

insights_prompt_template = PromptTemplate(
    template="""
    You are an excellent data analyst. Based on the following information, analyze the question, the generated SQL query, and the results obtained from the database. Provide an interpretation of the results ONLY and give a detailed explanation in the format below.

    Question: {input}
    SQL Query: {sql_query}
    Results from Database: {output}

    Interpretation:
    """,
    input_variables=["input", "sql_query", "output"]
)


error_handling_prompt_template = PromptTemplate(
    template= """
    You are an expert in SQL query generation. The following SQL query has encountered an error.
    
    **Failed SQL Query:**  
    {failed_query}  

    **Error Message:**  
    {error}  

    Carefully analyze the error and modify the query to fix the issue while maintaining the intent of the original question.
    Strictly specify  **Corrected SQL Query:**  before giving the corected query.
    **Corrected SQL Query:**  
    """,
    input_variables=["failed_query", "error"]
)