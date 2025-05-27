import json
import os
import re
import tempfile
from pathlib import Path

import pdfplumber
from docx import Document
from fastapi import File, UploadFile
from langchain.schema import HumanMessage, SystemMessage
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import VertexAIEmbeddings

from src.agent import prompts
from src.agent.schemas import GenerateIssueListRes
from src.auth import service as auth_service
from src.config.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GOOGLE_APPLICATION_CREDENTIALS,
    VERTEX_EMBEDDING_MODEL,
    VERTEX_PROJECT_ID,
)
from src.issue.schemas import IssueRes
from src.models import IssueRescheduling, Project, User
from src.response.error_definitions import (
    InvalidFileType,
    IssueGenerateError,
    ParseJsonFromResponseError,
    RepositoryNotFoundInGitHub,
)
from src.stat import service as stat_service

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

embedding = VertexAIEmbeddings(model_name=VERTEX_EMBEDDING_MODEL, project=VERTEX_PROJECT_ID)
vector_db = Chroma(persist_directory="chroma_db", embedding_function=embedding)
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=0,
    google_api_key=GEMINI_API_KEY
)

decomposition_chain = llm | prompts.decomposition_prompt_template


def add_text_data_tool(texts: list, metadatas: list):
    """
    Add data to the vector database.
    """
    vector_db.add_texts(texts, metadatas=metadatas)


def add_image_data_tool(images: list, metadatas: list):
    """
    Add image data to the vector database.
    """
    vector_db.add_images(images, metadatas=metadatas)


def search_data_tool(query: str, k: int = 2) -> list:
    """
    Search for similar data in the vector database.
    """
    results = vector_db.similarity_search(query, k=k)
    return results


async def decompose_task_tool(prompt: str) -> list:
    """
    Decomposes the input prompt into actionable steps.
    """
    steps_str = str(decomposition_chain.invoke(prompt))

    steps_list = [line.strip() for line in steps_str.split("\n") if line.strip()]
    return steps_list


async def create_rag_prompt_tool(original_prompt: str, context: str) -> str:
    """
    Create a RAG (Retrieval-Augmented Generation) prompt using the original prompt and context.
    """
    rag_prompt = prompts.rag_prompt_template.format(
        original_prompt=original_prompt,
        context=context
    )
    
    return rag_prompt


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


async def define_features(project_info: dict, design_documents: str) -> dict:
    """
    Define features based on design documents and feature example.
    """

    llm_response = await communicate_with_llm_tool(prompts.define_feature_template.format(
        project_info=project_info,
        documents= design_documents,
        example= prompts.feature_example
    ))

    features = dict()
    llm_response = llm_response.replace("```json", "")
    llm_response = llm_response.replace("```", "")
    llm_response = llm_response.replace("\n", "")
    llm_response = llm_response.replace('"  ', '"')
    llm_response = llm_response.replace("[", "")
    llm_response = llm_response.replace("]", "")
    llm_response = llm_response.split(",")
    for i in range(len(llm_response)):
        llm_response[i] = llm_response[i].replace('"', "")
        features[i] = llm_response[i][1:]
    return features


async def make_issues(project_info: dict, design_documents: str, features: dict):
    """
    Make issues based on features.
    """
    
    if(len(features) >= 5):
        interval = 5
    else:
        interval = len(features)

    for i in range(0, len(features), interval):
        issues = await communicate_with_llm_tool(prompts.make_issue_template.format(
            project_info=project_info,
            documents=design_documents,
            issue_template=prompts.issue_template,
            features=list(features.values())[i:i+interval]
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

            yield issue


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


async def get_github_activation_info(selected_repo_names: list[str], token: str):
    """
    Get GitHub information using the agent executor.
    """
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


async def assess_with_data(user: User, github_activation_data: list):
    """
    Assess the competency of a user based on their GitHub activity.
    """
    competency = await communicate_with_llm_tool(prompts.define_stat_prompt.format(
        user_name=user.github_name,
        criteria_table=prompts.score_table,
        github_activation_data=github_activation_data,
        info_file=prompts.info_file,
        output_example=prompts.define_stat_output_example
    ))

    competency = extract_json_dict_from_response(competency)
    
    competency_data = {
        "Name": competency["Name"],
        "Field": competency["Field"],
        "Experience" : competency["Experience"],
        "evaluation_scores": competency["evaluation_scores"],
        "implemented_features": competency["implemented_features"]
    }

    return competency_data


async def recommend_assignees_for_issues(project_info: Project, user_stat_list: list[str], issues: GenerateIssueListRes):
    """
    Recommend assignees for issues based on their competency.
    """

    assigned_issues = list()
    if(len(issues.issues) >= 10):
        interval = 10
    else:
        interval = len(issues.issues)

    for i in range(0, len(issues.issues), interval):
        response = await communicate_with_llm_tool(prompts.assign_issue_template.format(
            input_file=prompts.assign_input_template.format(
                project_name=project_info.name,
                project_overview="project overview",
                issues=issues.issues[i:i+interval],
                stats=user_stat_list
            ),
            output_example=prompts.assign_output_example
        ))

        response = extract_json_dict_from_response(response)
        
        assigned_issues.extend(response)
    return assigned_issues


async def get_feedback(project: Project, user_stat_list: list[str], issue_rescheduling: IssueRescheduling, issue: IssueRes):
    """
    Get feedback for issue rescheduling.
    """
    feedback = await communicate_with_llm_tool(prompts.feedback_template.format(
        project_info=json.dumps(project, ensure_ascii=False),
        reason=issue_rescheduling.reason,
        issue=json.dumps(issue, ensure_ascii=False),
        stats=user_stat_list,
        output_example=prompts.feedback_output_example
    ))

    feedback = extract_json_dict_from_response(feedback)

    return feedback