from dotenv import load_dotenv
load_dotenv()
from llm_commons.langchain.proxy import ChatOpenAI
from langchain.schema.messages import HumanMessage
from langchain.schema import SystemMessage
from llm_commons.langchain.proxy import init_llm
import os

messages = [
    HumanMessage(content="Say this is a test"),
]

aic_llm = ChatOpenAI(proxy_model_name='gpt-4-32k')
print(aic_llm.invoke(messages))