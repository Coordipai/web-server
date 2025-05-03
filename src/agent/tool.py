from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_chroma import Chroma
from src.agent import prompts
from src.config.config import GEMINI_MODEL, GEMINI_API_KEY, VERTEX_EMBEDDING_MODEL, VERTEX_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS
import json
from pathlib import Path
from fastapi import UploadFile, File
import tempfile
import pdfplumber
from docx import Document
from langchain_google_vertexai import VertexAIEmbeddings
import os
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
        SystemMessage(content="You are a professional project manger"),
        HumanMessage(content=prompt)
    ]
    response = await llm.agenerate([message])
    
    return response.generations[0][0].text


async def define_features(design_documents: str) -> dict:
    """
    Define features based on design documents and feature example.
    """

    llm_response = await communicate_with_llm_tool(prompts.define_feature_template.format(
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
    print(features)
    return features


async def make_issues(design_documents: str, features : dict):
    """
    Make issues based on features.
    """
    issue_list = list()
    if(len(features) >= 10):
        interval = 10
    else:
        interval = len(features)

    for i in range(0, len(features), interval):
        issues = await communicate_with_llm_tool(prompts.make_issue_template.format(
            documents=design_documents,
            issue_template=prompts.issue_template,
            features=list(features.values())[i:i+interval]
        ))
        issues = issues.replace("```json", "")
        issues = issues.replace("```", "")
        issues = json.loads(issues)

        issue_list.extend(issues)

    return issue_list


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
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")
        # TODO: Handle other file types if needed

    return text

