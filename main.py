import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
load_dotenv()

from trade import TradeTool

llm = ChatOpenAI(
  model="gpt-3.5-turbo-0613",
  temperature=0,
  openai_api_key=os.getenv("OPENAI_API_KEY"),
)

tools = [
  # DecimalTool(),
  TradeTool()
]

agent = initialize_agent(
  tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True
)


# result = agent.run("sell 0.147317315954412111 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
# result = agent.run("buy 0.01eth 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 ")

# print(result)


