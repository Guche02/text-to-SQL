import os
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from tools.database_tools import  execute_query, execute_modify_query
from tools.retriever_tool import retrieve_schema
from tools.llm_tools import generate_sql_query, generate_insights, handle_errors
from utils.prompts import (
    insights_prompt_template,
    insert_sql_gen_prompt_template,
)
from dotenv import load_dotenv
import pandas as pd

load_dotenv(os.path.join(os.path.dirname(__file__), "./configs/.env"))
api_key = os.getenv("MISTRAL_API_KEY")

llm = init_chat_model("mistral-medium", model_provider="mistralai", temperature=0.3, mistral_api_key=api_key)

retriever = RunnableLambda(lambda x: {"schema_info": retrieve_schema(f"{x['question']} + {x['data']}"), "question": x["question"], "data": x["data"]})

intermediate_results2 = []

def generate_insights_from_intermediate(intermediate_results):
    """
    Extracts relevant data from intermediate results and generates insights.
    """
    relevant_data = {}
    for res in intermediate_results:
        if res['step'] == "Human Message":
            relevant_data["input"] = res['result']
        elif res['step'] == "AI parsed_sql_query":
            relevant_data["sql_query"] = res['result']  
        elif res['step'] == "Raw DB Query Result":
            relevant_data["output"] = res.get("result", res)  
            relevant_data["columns"] = res.get("columns", [])  
    
    insights_input = insights_prompt_template.format(**relevant_data)
    print(insights_input)

    result = llm.invoke(insights_input)
    return result

chain2 = (
        retriever 
        | RunnableLambda(lambda x: intermediate_results2.append({"step": "Human Message", "result": x}) or x)  
        | insert_sql_gen_prompt_template
        | llm
        | StrOutputParser()
        | RunnableLambda(lambda x: intermediate_results2.append({"step": "AI llm_output", "result": x}) or x)
        | RunnableLambda(lambda x: print(f"\nGenerated SQL Query:\n{x}") or x)
        | StrOutputParser()
        | RunnableLambda(lambda sql_query: intermediate_results2.append({"step": "AI parsed_sql_query", "result": sql_query.replace("\\", "")}) or sql_query)
        | RunnableLambda(lambda sql_query: execute_modify_query(sql_query.replace("\\", "")))
        | RunnableLambda(lambda result: print(f"\nRaw Result obtained from DB:\n{result}") or result)
        | RunnableLambda(lambda result: (
            intermediate_results2.append({
                "step": "Raw DB Query Result",
                "result": result.get("result", result),  
                "columns": result.get("columns", [])  
            }) or result
        ))
        | RunnableLambda(lambda x: generate_insights_from_intermediate(intermediate_results2))  
        | StrOutputParser()  
    )

# query = """ insert the following data into the staff table"""

# data =  """ 
# first_name, last_name, store_id,address_id,username,password
# test1, subedy,1,2,test,12345
# test2, subedy,1,2,test,12345
# test3, subedy,1,2,test,12345
# """

# print(retrieve_schema(f"{query} and {data}"))

# try:
#         response = chain2.invoke({"question": query, "data": data})
#         print(f"\nFinal Query Result:\n{response}")
# except httpx.HTTPStatusError as e:
#         if e.response.status_code == 429:
#             print("\nRequest rate limited. Please try again later.")
#             response = "Request rate limited. Please try again later."
#         else:
#             print(f"\nAn unexpected error occurred: {str(e)}")
#             response = f"An unexpected error occurred: {str(e)}"

# print(intermediate_results2)
