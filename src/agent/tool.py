from langchain.agents import Tool, initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Qdrant
from langchain.chains import LLMChain
from langchain_core.tools import tool
from src.agent import prompts

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_output_tokens=200,
    google_api_key="AIzaSyAXsfG3E5aiC51KUeUvxkf0vrmyeTfo5yA"
)
# embeddings = OpenAIEmbeddings(api_key="YOUR_OPENAI_API_KEY")

# vector_db = Qdrant.from_texts([], embeddings)

decomposition_chain = llm | prompts.decomposition_prompt_template

@tool
async def add_data_tool(data: list[str]) -> str:
    """
    Add data to the vector database.
    """
    return 0

@tool
async def search_data_tool(query: str, k: int = 3) -> str:
    """
    Search the vector database for relevant data.
    """
    return 0

@tool
async def decompose_task_tool(prompt: str) -> list:
    """
    Decomposes the input prompt into actionable steps.
    """
    # 벡터 DB에 쿼리 추가
    # vector_db.add_texts([prompt])
    
    # 작업 분해 체인 실행
    steps_str = str(decomposition_chain.invoke(prompt))

    steps_list = [line.strip() for line in steps_str.split("\n") if line.strip()]
    return steps_list

@tool
async def create_rag_prompt_tool(original_prompt: str, context: str) -> str:
    """
    Create a RAG (Retrieval-Augmented Generation) prompt using the original prompt and context.
    """
    rag_prompt = prompts.rag_prompt_template.format(
        original_prompt=original_prompt,
        context=context
    )
    
    return rag_prompt

@tool
async def communicate_with_llm_tool(prompt: str) -> str:
    """
    Communicates with the LLM using the provided prompt.
    """

    message = [
        SystemMessage(content="You are a professional assistant."),
        HumanMessage(content=prompt)
    ]
    response = await llm.agenerate([message])
    
    return response.generations[0][0].text

tools = [add_data_tool, search_data_tool, decompose_task_tool, create_rag_prompt_tool, communicate_with_llm_tool]
