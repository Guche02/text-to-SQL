import os
from langchain.chat_models import init_chat_model
from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
load_dotenv(os.path.join(os.path.dirname(__file__), "./configs/.env"))
api_key = os.getenv("MISTRAL_API_KEY")

llm = init_chat_model("mistral-medium", model_provider="mistralai", temperature=0.5, mistral_api_key=api_key)

prompt_template_1 = "What is your favorite color?"
prompt_1 = PromptTemplate(template=prompt_template_1)

prompt_template_2 = "Why do you like {color}?"
prompt_2 = PromptTemplate(input_variables=["color"], template=prompt_template_2)

chain_1 = llm.bind_tools([prompt_1], memory=memory)
chain_2 = llm.bind_tools([prompt_2], memory=memory)

sequential_chain = SequentialChain(
    chains=[chain_1, chain_2],
    input_variables=[],  
    output_variables=["response"],  
    memory=memory,
)

result = sequential_chain.run()
print(result["response"])