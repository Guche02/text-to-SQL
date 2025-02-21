from langchain.prompts import PromptTemplate

question_validation_prompt_template = """
You are an AI system capable of understanding natural language questions related to database queries.
Given the following question, determine if it is a valid question related to a database query. STRICTLY Return only True or False as a result. NO EXPLANATION.

Question: {question}

Response: 
Return only True or False. No additional text
If valid, return true if not valid return False.

Result: 

"""

insert_sql_gen_prompt_template = PromptTemplate(
    template="""
    You are an expert SQL Generator. Based on the provided database schema information, generate a syntactically correct SQL INSERT query.
    The query should be in a directly executable format in the SQL environment. 
    If the data is provided, insert the data according to the question else follow the instructions in provided in question only.
    DON'T GENERATE ANY NOTES

    Schema Information:
    {schema_info}

    Question:
    {question}. Only generate query. No additional text. 

    Data:
    {data}

    SQL INSERT Query:
    """,
    input_variables=["schema_info", "question", "data"]
)

delete_sql_gen_prompt_template = PromptTemplate(
    template="""
    You are an expert SQL Generator. Based on the provided database schema information, generate a syntactically correct SQL DELETE query.
    The query should be in a directly executable format in the SQL environment. 
    If the data is provided, delete the data according to the question. If no data is provided, follow the instructions in the question.
    DON'T GENERATE ANY NOTES

    Schema Information:
    {schema_info}

    Question:
    {question}. Only generate query. No additional text. 

    Data:
    {data}

    SQL DELETE Query:
    """,
    input_variables=["schema_info", "question", "data"]
)


sql_gen_prompt_template = PromptTemplate(
    template="""
    You are an expert SQL Generator. Based on the provided database schema information, generate a syntactically correct SQL query. LIMIT each generated query upto only 30 results.
     !!!! STRICTLY generate the SQL query and no additional text and no placeholders. !!!!

    Schema Information:
    {schema_info}

    Question:
    {question}

    SQL Query:
    """,
    input_variables=["schema_info", "question"]
)

query_classifier_prompt_template = PromptTemplate(
    template="""
    You are an expert SQL Query Classifier. Classify the given SQL query into one of the following types: SELECT, INSERT, DELETE. STRICTLY return only the type without any additional text.

    SQL Query:
    {query}

    Query Type:
    """,
    input_variables=["query"]
)

insights_prompt_template = PromptTemplate(
    template="""
    You are an excellent data analyst. Based on the following information, analyze the question, the generated SQL query, and the results obtained from the 
    database. Provide an interpretation of the results ONLY and give a detailed explanation in the format below.

    Question: {input}
    SQL Query: {sql_query}
    Results from Database: {output}

    Answer:
    SQL Query used - "" \n
    Result obtained - "" \n
    Insights - ""
    """,
    input_variables=["input", "sql_query", "output"]
)

error_handling_prompt_template = PromptTemplate(
    template= """
    You are an expert in SQL query generation. The following SQL query has encountered an error.

    ***Input prompt:***
    {question}
    
    **Failed SQL Query:**  
    {failed_query}  

    **Error Message:**  
    {error}  

    Carefully analyze the error and modify the query to fix the issue while maintaining the intent of the original question. If a corrected query cannot be generated, simply mention that it cannot be generated. 

    **Corrected SQL Query:**
    """,
    input_variables=["failed_query", "error"]
)