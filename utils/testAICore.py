
from llm_commons.langchain.proxy import ChatOpenAI
from langchain.schema.messages import HumanMessage
from langchain.schema import SystemMessage
from llm_commons.langchain.proxy import init_llm
from dotenv import load_dotenv
load_dotenv()

llm = init_llm('gpt-4-32k', temperature=0, max_tokens=5000)

messages = [
    HumanMessage(content="Say this is a test"),
]

aic_llm = ChatOpenAI(proxy_model_name='gpt-4-32k')
print(aic_llm.invoke(messages))