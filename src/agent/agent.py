import json
import os
import re
import tempfile
from pathlib import Path

import pdfplumber
from docx import Document
from fastapi import File, UploadFile
from fastapi.datastructures import UploadFile as FastUploadFile
from langchain.agents import AgentType, initialize_agent
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import VertexAIEmbeddings
from sqlalchemy.orm import Session

from src.agent import aprompt, prompts
from src.agent.schemas import GenerateIssueListRes, GenerateIssueRes
from src.auth import service as auth_service
from src.config.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GOOGLE_APPLICATION_CREDENTIALS,
    VERTEX_EMBEDDING_MODEL,
    VERTEX_PROJECT_ID,
)
from src.config.database import get_db
from src.issue import repository as issue_repository
from src.project import repository as project_repository
from src.response.error_definitions import (
    DesignDocNotFound,
    InvalidFileType,
    IssueGenerateError,
    IssueNotFound,
    ParseJsonFromResponseError,
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


async def communicate_with_llm_tool(prompt: str) -> str:
    """
    Communicates with the LLM using the provided prompt.
    """

    message = [
        SystemMessage(content="You are a professional project manager"),
        HumanMessage(content=prompt)
    ]
    response = await llm.agenerate([message])
    
    return response.generations[0][0].text


def extract_json_dict_from_response(response_text: str) -> dict:
    """
    Extracts a JSON dictionary from the response text.
    """
    pattern = r'```json(.*?)```'
    match = re.search(pattern, response_text, re.DOTALL)
    if not match:
        print("------------Invalid Output format------------")
        print(response_text)
        return {}
    json_str = match.group(1)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ParseJsonFromResponseError()


@tool("get_project_info")
async def get_project_info(project_id: int) -> dict:
    """프로젝트 ID를 받아 프로젝트 정보를 반환합니다."""

    db: Session = next(get_db())  # 데이터베이스 세션을 가져옵니다
    project = project_repository.find_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFound()
    
    return {
        "name": project.name,
        "owner": project.owner,
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


@tool("get_github_activation_data")
async def get_github_activation_data(user_id: int) -> list:
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


@tool("get_user_info")
async def get_user_info(user_id: int) -> dict:
    """사용자 ID를 받아 사용자 정보를 반환합니다."""
    
    db: Session = next(get_db())
    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise UserNotFound()
    
    return {
        "name": user.name,
        "github_name": user.github_name,
        "github_id": user.github_id,
        "category": user.category,
        "career": user.career
    }


@tool("get_users_of_project")
async def get_users_of_project(project_id: int) -> list:
    """프로젝트 ID를 받아 해당 프로젝트의 사용자 정보를 반환합니다."""
    
    db: Session = next(get_db())
    project = project_repository.find_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFound()
    
    users = []
    for project_user in project.members:
        user = user_repository.find_user_by_user_id(db, project_user.user_id)
        if user:
            users.append({
                "user_id": user.id,
                "name": user.name,
                "github_name": user.github_name,
                "category": user.category,
                "career": user.career
            })
    
    return users


@tool("save_user_stat")
async def save_user_stat(user_id: int, stat: dict) -> str:
    """사용자 ID와 통계 정보를 받아 사용자 역량 정보를 저장합니다."""
    
    db: Session = next(get_db())
    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise UserNotFound()
    
    user.stat = stat
    user_repository.update_user_stat(db, user)
    
    return "User statistics updated successfully."


@tool("get_user_stat")
async def get_user_stat(user_id: int) -> dict:
    """사용자 ID를 받아 사용자 역량 정보를 반환합니다."""
    
    db: Session = next(get_db())
    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise UserNotFound()
    
    return {
        "name": user.name,
        "github_name": user.github_name,
        "stat": user.stat,
        "category": user.category,
        "career": user.career
    }


@tool("get_issue_rescheduling_info")
async def get_issue_rescheduling_info(issue_id: int) -> dict:
    """이슈 ID를 받아 이슈 재조정 정보를 반환합니다."""
    
    db: Session = next(get_db())
    issue = project_repository.find_issue_by_id(db, issue_id)
    if not issue:
        raise ProjectNotFound()
    
    return {
        "issue_number": issue.issue_number,
        "reason": issue.reason,
        "new_iteration": issue.new_iteration,
        "new_assignees": issue.new_assignees,
        "project_id": issue.project_id
    }


@tool("get_issue_to_be_rescheduled")
async def get_issue_to_be_rescheduled(project_info: dict, issue_id: int) -> dict:

    """프로젝트 정보와 이슈 ID를 받아 이슈 재조정 정보를 반환합니다."""
    db: Session = next(get_db())

    # Get issue information from database
    issue = issue_repository.find_issue_by_issue_number(
        project_info["owner"], project_info["repo_fullname"], issue_id, db
    )
    if not issue:
        raise IssueNotFound()

    return {
        "repo_fullname": project_info["repo_fullname"],
        "issue_number": issue.issue_number,
        "title": issue.title,
        "body": issue.body,
        "assignees": [assignee.github_name for assignee in issue.assignees],
        "priority": issue.priority,
        "iteration": issue.iteration,
        "labels": [label.name for label in issue.labels],
        "closed": issue.closed
    }


@tool("make_issues")
async def make_issues(project_info: dict, design_documents: str, features: list):
    """
    Make issues based on features.
    """
    
    if(len(features) >= 5):
        interval = 5
    else:
        interval = len(features)

    generated_issues = list()
    for i in range(0, len(features), interval):
        issues = await communicate_with_llm_tool(prompts.make_issue_template.format(
            project_info=project_info,
            documents=design_documents,
            issue_template=prompts.issue_template,
            features=features[i:i+interval]
        ))
        if not issues:
            raise IssueGenerateError()
        
        issues = extract_json_dict_from_response(issues)
        
        for issue in issues:
            # check if issue contains "type", "name", "description", "title", "labels", "sprint", "body"
            if not all(key in issue for key in ["type", "name", "description", "title", "labels", "sprint", "body"]):
                print("------------Invalid issue format------------")
                print(issue)
                raise IssueGenerateError()
            generated_issues.append(GenerateIssueRes.from_issue(issue))

    
    return GenerateIssueListRes(issues=generated_issues)


@tool("get_issue_list")
async def get_issue_list() -> list:
    """ Get a list of issues """
    issues = json.loads(aprompt.made_issue_example)
    return issues


@tool("assess_with_data")
async def assess_with_data(user_info: dict, github_activation_data: list):
    """
    Assess the competency of a user based on their GitHub activity.
    """
    competency = await communicate_with_llm_tool(prompts.define_stat_prompt.format(
        user_name=user_info["name"],
        criteria_table=prompts.score_table,
        github_activation_data=github_activation_data,
        info_file=prompts.info_file,
        output_example=prompts.define_stat_output_example
    ))

    competency = extract_json_dict_from_response(competency)

    return competency


@tool("recommend_assignees_for_issues")
async def recommend_assignees_for_issues(project_info: dict, user_stat_list: list, issues: list):
    """
    Recommend assignees for issues based on their competency.
    """
    
    assigned_issues = list()
    if(len(issues) >= 10):
        interval = 10
    else:
        interval = len(issues)

    for i in range(0, len(issues), interval):
        response = await communicate_with_llm_tool(prompts.assign_issue_template.format(
            input_file=prompts.assign_input_template.format(
                project_name=project_info["name"],
                project_overview="project overview",
                # issues=issues.issues[i:i+interval],
                issues=issues[i:i+interval],
                stats=user_stat_list
            ),
            output_example=prompts.assign_output_example
        ))

        response = extract_json_dict_from_response(response)
        
        assigned_issues.extend(response)
    return assigned_issues


@tool("get_feedback")
async def get_feedback(project_info: dict, user_stat_list: list, issue_rescheduling_info: dict, issue_info: dict):
    """
    Get feedback for issue rescheduling.
    """
    feedback = await communicate_with_llm_tool(prompts.feedback_template.format(
        project_info=project_info,
        reason=issue_rescheduling_info["reason"],
        issue= issue_info,
        stats=user_stat_list,
        output_example=prompts.feedback_output_example
    ))

    feedback = extract_json_dict_from_response(feedback)

    return feedback


TOOLS = [
    get_project_info, 
    get_document_info, 
    get_issue_template, 
    get_github_activation_data, 
    get_user_info, 
    save_user_stat, 
    get_user_stat, 
    get_users_of_project, 
    get_issue_rescheduling_info, 
    get_issue_to_be_rescheduled,
    make_issues,
    assess_with_data,
    recommend_assignees_for_issues,
    get_feedback
] 


agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prefix": "안녕하세요, 저는 당신의 개인 비서입니다."},
    verbose=True
)



