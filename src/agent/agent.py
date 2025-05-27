import json
import os
import tempfile
from pathlib import Path

import pdfplumber
from docx import Document
from fastapi import File, UploadFile
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import VertexAIEmbeddings
from sqlalchemy.orm import Session

from src.agent import prompts
from src.auth import service as auth_service
from src.config.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GOOGLE_APPLICATION_CREDENTIALS,
    VERTEX_EMBEDDING_MODEL,
    VERTEX_PROJECT_ID,
)
from src.config.database import get_db
from src.project import repository as project_repository
from src.response.error_definitions import (
    DesignDocNotFound,
    InvalidFileType,
    ProjectNotFound,
    RepositoryNotFoundInGitHub,
    UserNotFound,
)
from src.stat import service as stat_service
from src.user import repository as user_repository
from src.user_repository import service as user_repository_service

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

embedding = VertexAIEmbeddings(model_name=VERTEX_EMBEDDING_MODEL, project=VERTEX_PROJECT_ID)
vector_db = Chroma(persist_directory="chroma_db", embedding_function=embedding)
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=0,
    google_api_key=GEMINI_API_KEY
)

def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()


def extract_text_from_docx(docx_path: Path) -> str:
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()


def extract_text_from_json(json_path: Path) -> str:
    with open(json_path, 'r') as file:
        data = json.load(file)
    return json.dumps(data, ensure_ascii=False, indent=4)


async def extract_text_from_documents(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    if suffix == ".pdf":
        text = extract_text_from_pdf(tmp_path)
    elif suffix == ".docx":
        text = extract_text_from_docx(tmp_path)
    elif suffix == ".json":
        text = extract_text_from_json(tmp_path)
    else:
        raise InvalidFileType()
        # TODO: Handle other file types if needed

    return text



from fastapi.datastructures import UploadFile as FastUploadFile

# ── 1) 필수 import ─────────────────────────────────────────────
from langchain.agents import AgentType, initialize_agent

# ────────────────────────────────────────────────────────────────


# ── 2) Agent 가 사용할 Tool 정의 ────────────────────────────────

@tool("get_project_info")
async def get_project_info(project_id: int) -> dict:
    """프로젝트 ID를 받아 프로젝트 정보를 반환합니다."""

    db: Session = next(get_db())  # 데이터베이스 세션을 가져옵니다
    project = project_repository.find_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFound
    
    return {
        "name": project.name,
        "repo_fullname": project.repo_fullname,
        "start_date": project.start_date.strftime("%Y-%m-%d %H:%M:%S") if project.start_date else None,
        "end_date": project.end_date.strftime("%Y-%m-%d %H:%M:%S") if project.end_date else None,
        "sprint_unit": project.sprint_unit
    }


@tool("get_document_info")
async def get_document_info(project_name: str) -> list:
    """프로젝트 이름을 받아 해당 프로젝트의 문서 정보를 반환합니다."""

    project_dir = os.path.join("design_docs", project_name)
    file_names = os.listdir(project_dir)
    if not file_names:
        raise DesignDocNotFound()
    
    files = [os.path.join(project_dir, file_name) for file_name in file_names]

    extracted_texts = ""
    for file in files:
        # Load documents with file path (pdf, docx)
        file_path = Path(file)
        with open(file_path, "rb") as f:
            upload_file = FastUploadFile(filename=file_path.name, file=f)
            text = await extract_text_from_documents(upload_file)
            extracted_texts += file_path.name
            extracted_texts += "\n"
            extracted_texts += text
            extracted_texts += "\n\n"
        
    return extracted_texts


@tool("get_issue_template")
async def get_issue_template() -> str:
    """이슈 템플릿을 반환합니다."""
    return str(prompts.issue_template)


@tool("get_github_activation_info")
async def get_github_activation_info(user_id: int):
    """
    Get GitHub information using the agent executor.
    """

    db: Session = next(get_db())
    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise UserNotFound()
    
    token = user.github_access_token
    selected_repo_names = user_repository_service.get_all_selected_repositories(user_id, db)
    repo_list = stat_service.get_repositories(token)

    # get user name from token
    user_info = await auth_service.get_github_user_info(token)
    user_name = user_info["login"]

    repo_names_from_github = [repo["name"] for repo in repo_list]
    for selected_repo in selected_repo_names:
        if selected_repo.repo_fullname not in repo_names_from_github:
            raise RepositoryNotFoundInGitHub(selected_repo.repo_fullname)
    
    selected_repo_list = [repo for repo in repo_list if repo["name"] in [repo.repo_fullname for repo in selected_repo_names]]

    for selected_repo in selected_repo_list:
        prs = stat_service.get_pull_requests(selected_repo["name"], user_name, token)
        commits = stat_service.get_commits(selected_repo["name"], user_name, token)
        selected_repo["prs"] = prs
        selected_repo["commits"] = commits

    return selected_repo_list


# ── 3) Agent 가 접근할 수 있는 도구 목록 정의 ────────────────
TOOLS = [get_project_info, get_document_info, get_issue_template, get_github_activation_info]         # Agent 가 접근할 수 있는 도구 목록
# ────────────────────────────────────────────────────────────────


# ── 4) Agent 초기화 (initialize_agent) ─────────────────────────
agent = initialize_agent(
    tools=TOOLS,                     # ① 사용할 Tool 리스트
    llm=llm,                         # ② 기반 LLM
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # ③ Agent 유형
    agent_kwargs={"prefix": "안녕하세요, 저는 당신의 개인 비서입니다."},  # Agent 의 추가 설정
    verbose=True                     # ④ 디버깅용 출력
)
# ────────────────────────────────────────────────────────────────



