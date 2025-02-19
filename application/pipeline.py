import os
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from tools.database_tools import extract_corrected_sql, execute_query
from tools.retriever_tool import retrieve_schema
from tools.llm_tools import generate_sql_query, generate_insights, handle_errors
from utils.prompts import sql_gen_prompt_template, error_handling_prompt_template, insights_prompt_template, question_validation_prompt_template
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "./configs/.env"))
api_key = os.getenv("MISTRAL_API_KEY")

llm = init_chat_model("mistral-medium", model_provider="mistralai", temperature=0.5, mistral_api_key=api_key)

validate_question = RunnableLambda(lambda x: question_validation_prompt_template.format(question=x["question"]))
retriever = RunnableLambda(lambda x: {"schema_info": retrieve_schema(x["question"]), "question": x["question"]})
generate_sql = RunnableLambda(lambda x: generate_sql_query(x["schema_info"], x["question"]))
execute_sql = RunnableLambda(lambda x: execute_query(x))
generate_insights_step = RunnableLambda(lambda x: generate_insights(x))
handle_errors_step = RunnableLambda(lambda x: handle_errors(x))

passfunc = RunnableLambda(lambda res: {"result": res["result"]})

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
        "result": x["result"].replace("\\", "")  
    })  
    | RunnableLambda(lambda x: (print("\nCorrected SQL Query:\n", x["result"]), x)[-1])   
    | RunnableLambda(lambda x: {
        "success": False, 
        "result": execute_query(x["result"])  
    })
)


intermediate_results = []

def generate_insights_from_intermediate(intermediate_results):
    relevant_data = {}
    for res in intermediate_results:
        if res['step'] == "Human Message":
            relevant_data["input"] = res['result']
        elif res['step'] == "AI parsed_sql_query":
            relevant_data["sql_query"] = res['result']  
        elif res['step'] == "final_result":
            relevant_data["output"] = res['result']
    
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
    | RunnableLambda(lambda sql_query: execute_query(sql_query.replace("\\", "")))  
    | RunnableLambda(lambda result: intermediate_results.append({"step": "AI db_query_result", "result": result}) or result)  
    | RunnableBranch(
        (lambda res: res.get("success", True), passfunc),  
        failfunc
    )
    | RunnableLambda(lambda result: print(f"\nRaw Result obtained from DB:\n{result}") or result)   
    | RunnableLambda(lambda result: intermediate_results.append({"step": "final_result", "result": result}) or result)  
    | RunnableLambda(lambda x: generate_insights_from_intermediate(intermediate_results))  
    | StrOutputParser()  
)

query = """ 
Retrieve the full name of customers, their email, the films they have rented, the category of each film, and the store where they rented the film from. Ensure the results include the rental date and the amount paid by the customer.
"""

# # query = """
# # Hi
# # """

response = chain.invoke({"question": query})
print(f"\nFinal Query Result:\n{response}")