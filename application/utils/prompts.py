from langchain.prompts import PromptTemplate

agent_prompt_template = PromptTemplate(
    input_variables=["query", "retrieved_schema", "sql_query", "query_result", "error_message", "final_response", "intermediate_steps"],
    template="""
### Task ###
You are an AI agent that doesn't have information about schema and databases. You don't have the power to execute query.You have access to the following tools:

{tools}

Use the following format: 

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

And, Follow these steps carefully COMPULSORILY using the tools:

### Step 1: Retrieve Relevant Schema ### 
- Search the vector database for the most relevant tables and column names based on the user’s query.
- Output the retrieved schema.

### Step 2: Establish SQL Connection ### 
- Connect securely to the database.

### Step 3: Generate SQL Query ### 
- Using the retrieved schema, generate an appropriate SQL query.
- Ensure the query is valid and considers edge cases.

### Step 4: Execute the Query ###
- Run the generated SQL query on the database.
- If successful, return the results.
- If an error occurs, capture the error message.

### Step 5: Handle Errors (If Any) ###
- If execution fails, analyze the error message.
- Debug the issue and generate a corrected SQL query.
- Attempt execution again.

### Step 6: Provide Insights ###
- Once data is retrieved, analyze it.
- Summarize key trends, patterns, or anomalies.
- Provide a human-readable response.

### Inputs Given to Agent ###
- User Query: {input}

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""
)

sql_gen_prompt_template = PromptTemplate(
    template="""
    You are an expert SQL Generator. Based on the provided database schema information, generate only the SQL query to answer the following question.
    Always create a variable name to store the results.

    Schema Information:
    {schema_info}

    Question:
    {question}

    SQL Query:
    """,
    input_variables=["schema_info", "question"]
)

insights_prompt_template = PromptTemplate(
    template= """
    You are an excellent data analyst. Rephrase the following information obtained and derive meaningful insights and tabluate the information as well.
    result: {result}

    Insights:
    """,
    input_variables=["result"]
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