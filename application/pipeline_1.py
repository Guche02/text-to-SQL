import os
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from tools.database_tools import extract_corrected_sql, execute_select_query
from tools.retriever_tool import retrieve_schema
from tools.llm_tools import generate_sql_query, generate_insights, handle_errors
from utils.prompts import (
    sql_gen_prompt_template,
    error_handling_prompt_template,
    insights_prompt_template,
    question_validation_prompt_template,
)
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "./configs/.env"))
api_key = os.getenv("MISTRAL_API_KEY")

llm = init_chat_model("mistral-medium", model_provider="mistralai", temperature=0.3, mistral_api_key=api_key)

validate_question = RunnableLambda(lambda x: question_validation_prompt_template.format(question=x["question"]))
retriever = RunnableLambda(lambda x: {"schema_info": retrieve_schema(x["question"]), "question": x["question"]})
generate_sql = RunnableLambda(lambda x: generate_sql_query(x["schema_info"], x["question"]))
generate_insights_step = RunnableLambda(lambda x: generate_insights(x))
handle_errors_step = RunnableLambda(lambda x: handle_errors(x))

passfunc = RunnableLambda(lambda res: {
    "result": res.get("result", res),  
    "columns": res.get("columns", [])
})


failfunc = (
    RunnableLambda(lambda x: (
        print("\nReceived Failed Query:", x.get('failed_query', '')),
        print("\nReceived Error Message:", x.get('error', '')),
        print("\nOriginal Input Prompt:", next(
            (res["result"] for res in intermediate_results if res["step"] == "Human Message"), ""
        )),
        x
    )[-1])  
    | RunnableLambda(lambda x: {
        "question": next(
            (res["result"] for res in intermediate_results if res["step"] == "Human Message"), ""
        ),  
        "failed_query": x.get("failed_query", ""),
        "error": x.get("error", ""),
        "message": x.get("message", "")
    })  
    | error_handling_prompt_template
    | RunnableLambda(lambda x: (print("\nError template Input:", x), x)[-1])
    | llm
    | RunnableLambda(lambda x: (print("Model output (Error Handling):", x), x)[-1])
    | RunnableLambda(lambda x: {
        "success": False,
        "result": extract_corrected_sql(x)  
    })  
    | RunnableLambda(lambda x: {
        "success": False, 
        "result": x["result"].replace("\\", "") if x["result"] is not None else "SQL Query not generated."
    })  
    | RunnableLambda(lambda x: (print("\nCorrected SQL Query:\n", x["result"]), x)[-1])   
    | RunnableLambda(lambda x: {
        "success": False, 
        "result": execute_select_query(x["result"])  if x["result"] is not None else "SQL query not generated."
    })
)

def retry_failfunc(x, retries=3):
    existing_failed_query = x.get("failed_query", "")
    existing_error = x.get("error", "")
    existing_message = x.get("message", "")
    existing_result = x.get("result", "")
    
    for attempt in range(retries):
        print(f"\nAttempt {attempt + 1} to correct the SQL query...")
        
        x = failfunc.invoke(x)
        new_failed_query = x.get("failed_query", "")
        if new_failed_query:
            existing_failed_query += f"\n[Attempt {attempt + 1}] {new_failed_query}"

        new_error = x.get("error", "")
        if new_error:
            existing_error += f"\n[Attempt {attempt + 1}] {new_error}"

        new_message = x.get("message", "")
        if new_message:
            existing_message += f"\n[Attempt {attempt + 1}] {new_message}"

        new_result = x.get("result", "")
        if new_result:
            existing_result += f"\n[Attempt {attempt + 1}] {new_result}"

        intermediate_results.append({
            "step": f"FailFunc Attempt {attempt + 1}",
            "failed_query": existing_failed_query,
            "error": existing_error,
            "message": existing_message,
            "result": existing_result,
        })
        
        x["failed_query"] = existing_failed_query
        x["error"] = existing_error
        x["message"] = existing_message
        x["result"] = existing_result
        
        if x.get("success", False):  
            return x
    
    return x  


intermediate_results = []

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

chain = (
    validate_question  
    | RunnableLambda(lambda x: intermediate_results.append({"step": "Human Message", "result": x}) or x)  
    | RunnableLambda(lambda x: print(f"\nPrompt Input:\n{x}") or x)  
    | llm  
    | StrOutputParser()  
    | RunnableLambda(lambda x: {
        "valid": "True" in x,  
        "message": x  
    })
    | RunnableBranch(
        (lambda res: res["valid"],  
         RunnableLambda(lambda _: {"question": intermediate_results[0].get("result", "")}) 
         | retriever 
         | sql_gen_prompt_template  
        ),  
        RunnableLambda(lambda x: f"Not a valid question for generating an SQL query. Reason: {x['message']}")  
    )
    | llm  
    | StrOutputParser()  
    | RunnableLambda(lambda x: intermediate_results.append({"step": "AI llm_output", "result": x}) or x)  
    | RunnableLambda(lambda x: print(f"\nGenerated SQL Query:\n{x}") or x)  
    | StrOutputParser()  
    | RunnableLambda(lambda sql_query: intermediate_results.append({"step": "AI parsed_sql_query", "result": sql_query.replace("\\", "")}) or sql_query)  
    | RunnableLambda(lambda sql_query: execute_select_query(sql_query.replace("\\", "")))  
    | RunnableLambda(lambda result: print(f"\nRaw Result obtained from DB:\n{result}") or result)   
    | RunnableLambda(lambda result: (
        intermediate_results.append({
            "step": "Raw DB Query Result",
            "result": result.get("result", result),  
            "columns": result.get("columns", [])  
        }) or result
    ))
    | RunnableBranch(
        (lambda res: res.get("success", True), passfunc),  
        RunnableLambda(retry_failfunc)  
    )
    | RunnableLambda(lambda x: generate_insights_from_intermediate(intermediate_results))  
    | StrOutputParser()  
)

# query = """ list the top 30 movies present in the database
# """

# try:
#     response = chain.invoke({"question": query})
#     print(f"\nFinal Query Result:\n{response}")
# except httpx.HTTPStatusError as e:
#     if e.response.status_code == 429:
#         print("\nRequest rate limited. Please try again later.")
#         response = "Request rate limited. Please try again later."
#     else:
#         print(f"\nAn unexpected error occurred: {str(e)}")
#         response = f"An unexpected error occurred: {str(e)}"

# print(intermediate_results)