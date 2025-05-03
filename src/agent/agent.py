from langchain.agents import create_react_agent, AgentExecutor, ZeroShotAgent
from src.agent import tool, chain
from langchain import hub
from langchain.tools.render import render_text_description

# prompt = hub.pull("hwchase17/react").partial(
#     tools=render_text_description(tool.tools),
#     tool_names=", ".join([t.name for t in tool.tools]),
# )
# agent = create_react_agent(tool.llm, tool.tools, prompt)

# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tool.tools,
#     verbose=True,
#     handle_parsing_errors=True,
# )

####################################################################
# for test agent #