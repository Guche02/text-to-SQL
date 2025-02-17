import os
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from tools.database_tools import establish_mysql_connection, execute_query
from tools.retriever_tool import retrieve_schema
from tools.llm_tools import generate_sql_query, generate_insights, handle_errors
from utils.prompts import sql_gen_prompt_template, error_handling_prompt_template, insights_prompt_template
from langchain import hub
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "./configs/.env"))
api_key = os.getenv("MISTRAL_API_KEY")

llm = init_chat_model("mistral-medium", model_provider="mistralai", temperature=0.5, mistral_api_key=api_key)

retriever = RunnableLambda(lambda x: {"schema_info": retrieve_schema(x["question"]), "question": x["question"]})

generate_sql = RunnableLambda(lambda x: generate_sql_query(x["schema_info"], x["question"]))
connect_db = RunnableLambda(lambda x: establish_mysql_connection())
execute_sql = RunnableLambda(lambda x: execute_query(x))
generate_insights_step = RunnableLambda(lambda x: generate_insights(x))
handle_errors_step = RunnableLambda(lambda x: handle_errors(x))

def handle_retries(x):
    retry_count = x.get("retry_count", 0)
    
    if retry_count < 3:
        return {**x, "retry_count": retry_count + 1}
    else:
        return {
            "failed_query": x.get("failed_query", ""),
            "error": x.get("error", "SQL execution failed"),
            "message": "Sorry, I couldn't generate the query. Would you rephrase your question?"
        }

passfunc = RunnableLambda(lambda res: {"result": res["result"]})

failfunc = (
    RunnableLambda(handle_retries)  
    | RunnableLambda(lambda x: (
        print(f"\nAttempt {x['retry_count']} of 3"), x
    )[-1])  
    | RunnableLambda(lambda x: (
        print("\nReceived Failed Query:", x['failed_query']),
        print("\nReceived Error Message:", x['error']),
        print("\nMessage:", x['message']),  
        x
    )[-1])  
    | error_handling_prompt_template
    | RunnableLambda(lambda x: (print("\nError template:", x), x)[-1])
    | llm
    | RunnableLambda(lambda x: (print("Model output: ", x), x)[-1])
    | RunnableLambda(lambda x: {
        "success": False,
        "result": x.get("message", "")
    })  
)

chain = (
    retriever
    | sql_gen_prompt_template  
    | RunnableLambda(lambda x: print("Prompt Input:", x) or x)  
    | llm  
    | RunnableLambda(lambda x: print("Generated SQL Query:", x) or x)  
    | StrOutputParser()  
    | RunnableLambda(lambda sql_query: print("Cleaned SQL Query:", sql_query.replace("\\", "")) or sql_query)  
    | RunnableLambda(lambda sql_query: execute_query(sql_query.replace("\\", "")))  
    | RunnableBranch(
        (lambda res: "success" in res and res["success"], passfunc),  
        failfunc  
    )
    | RunnableLambda(lambda result: print("Raw Result obtained from DB:", result) or result)  
    | insights_prompt_template  
    | llm  
    | RunnableLambda(lambda insights: print("Final Insights:", insights) or insights)  
)

response = chain.invoke({
    "question": "how many films are there in the inventory?"
})

print(response)