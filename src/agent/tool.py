from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents import Tool

# LLM 및 임베딩 초기화 (각자의 API 키로 변경)
llm = OpenAI(api_key="YOUR_OPENAI_API_KEY", temperature=0.7)
embeddings = OpenAIEmbeddings(api_key="YOUR_OPENAI_API_KEY")

# 메모리 내 벡터 DB 생성
vector_db = Qdrant.from_texts([], embeddings)

# 작업 분해를 위한 프롬프트 템플릿 및 체인 생성
decomposition_template = PromptTemplate(
    input_variables=["prompt"],
    template=(
        "당신은 프로젝트 매니저 역할의 AI 에이전트입니다. "
        "아래의 작업을 실행 가능한 단계들로 분해하세요.\n\n"
        "작업: {prompt}\n\n"
        "단계:"
    )
)
decomposition_chain = LLMChain(llm=llm, prompt=decomposition_template)

# Tool 1: 데이터를 벡터 DB에 추가하는 도구
def add_data_tool(data: list[str]) -> str:
    return 0

# Tool 2: 벡터 DB에서 관련 데이터를 검색하는 도구
def search_data_tool(query: str, k: int = 3) -> str:
    return 0

# Tool 3: 입력 프롬프트를 실행 가능한 단계로 분해하는 도구
def decompose_task_tool(prompt: str) -> str:
    return 0

# Tool 4: 원본 프롬프트와 검색된 컨텍스트를 결합하여 RAG 프롬프트 생성 도구
def create_rag_prompt_tool(original_prompt: str, context: str) -> str:
    return 0

# Tool 5: LLM과 통신하여 응답을 받아오는 도구
def communicate_with_llm_tool(prompt: str) -> str:
    return 0

# LangChain 에이전트가 사용할 수 있도록 Tool 객체로 등록할 수 있습니다.
tools = [
    Tool(
        name="AddData",
        func=add_data_tool,
        description="벡터 DB에 데이터를 추가합니다. 입력은 문자열 리스트입니다."
    ),
    Tool(
        name="SearchData",
        func=search_data_tool,
        description="벡터 DB에서 쿼리와 관련된 데이터를 검색합니다. 입력은 검색 쿼리와 (선택적으로) 반환할 결과 수입니다."
    ),
    Tool(
        name="DecomposeTask",
        func=decompose_task_tool,
        description="입력 프롬프트를 실행 가능한 단계들로 분해합니다."
    ),
    Tool(
        name="CreateRAGPrompt",
        func=create_rag_prompt_tool,
        description="원본 프롬프트와 검색된 컨텍스트를 결합하여 RAG 프롬프트를 생성합니다."
    ),
    Tool(
        name="CommunicateLLM",
        func=communicate_with_llm_tool,
        description="LLM에게 프롬프트를 전달하여 응답을 받아옵니다."
    )
]