import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import File, UploadFile
from sqlalchemy.orm import Session

from project import repository
from project.schemas import ProjectListRes, ProjectReq, ProjectRes, ProjectUserRes
from src.models import Project, ProjectUser
from src.project_user.repository import (
    create_project_user,
    find_all_projects_by_user_id,
)
from src.response.error_definitions import (
    FileDeleteError,
    ProjectAlreadyExist,
    ProjectNotFound,
    ProjectOwnerMismatched,
)
from src.user.repository import find_user_by_user_id


async def create_project(
    user_id: int,
    project_req: ProjectReq,
    db: Session,
    files: Optional[List[UploadFile]] = File(None),
):
    """
    Create a new project

    Returns project data
    """
    existing_project = repository.find_project_by_name(db, project_req.name)

    if existing_project:
        raise ProjectAlreadyExist()

    design_doc_paths = await upload_file(project_req.name, files)

    project = Project(
        name=project_req.name,
        owner=user_id,
        repo_fullname=project_req.repo_fullname,
        start_date=project_req.start_date,
        end_date=project_req.end_date,
        sprint_unit=project_req.sprint_unit,
        discord_channel_id=project_req.discord_channel_id,
        design_doc_paths=design_doc_paths,
    )

    saved_project = repository.create_project(db, project)
    project_members = []

    for req_member in project_req.members:
        found_user = find_user_by_user_id(db, req_member.id)
        project_user = ProjectUser(
            user=found_user, project=saved_project, role=req_member.role
        )
        saved_project_user = create_project_user(db, project_user)
        project_member = ProjectUserRes.from_user(found_user, saved_project_user.role)
        project_members.append(project_member)

    owner_user = find_user_by_user_id(db, user_id)
    project_res = ProjectRes.from_project(saved_project, owner_user, project_members, design_doc_paths)

    # TODO Embedding project files
    # Check files exist
    # saved_files = await upload_file(saved_project.project_name, files)

    return project_res


def get_project(project_id: int, db: Session):
    """
    Get the existing project by project id

    Returns project data
    """
    existing_project = repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    owner_user = find_user_by_user_id(db, existing_project.owner)

    project_members = []
    for project_user in existing_project.members:
        found_user = find_user_by_user_id(db, project_user.user_id)
        project_member = ProjectUserRes.from_user(found_user, project_user.role)
        project_members.append(project_member)

    design_docs = list_files_in_directory(existing_project.name)
    project_res = ProjectRes.from_project(
        existing_project, owner_user, project_members, design_docs
    )

    return project_res


def get_all_projects(user_id: int, db: Session):
    """
    Get all existing projects that user owns or participates in

    Returns list of projects
    """
    owned_projects = repository.find_project_by_owner(db, user_id)
    participated_projects = find_all_projects_by_user_id(db, user_id)

    project_list = []
    added_project_ids = set()

    for project in owned_projects:
        if project.id not in added_project_ids:
            project_list.append(ProjectListRes.model_validate(project))
            added_project_ids.add(project.id)

    for project_user in participated_projects:
        project = repository.find_project_by_id(db, project_user.project_id)
        if project.id not in added_project_ids:
            project_list.append(ProjectListRes.model_validate(project))
            added_project_ids.add(project.id)

    return project_list


def update_project(
    project_id: int, project_req: ProjectReq, files: List[UploadFile], db: Session
):
    """
    Update the existing project by project id

    Returns project data
    """
    existing_project = repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    existing_project.name = (project_req.name,)
    existing_project.repo_fullname = (project_req.repo_fullname,)
    existing_project.start_date = (project_req.start_date,)
    existing_project.end_date = (project_req.end_date,)
    existing_project.sprint_unit = (project_req.sprint_unit,)
    existing_project.discord_channel_id = (project_req.discord_channel_id,)
    existing_project.design_doc_paths = (project_req.design_doc_paths,)

    saved_project = repository.update_project(db, existing_project)

    # TODO Embedding project files
    # saved_files = await upload_file(saved_project.project_name, files)

    owner_user = find_user_by_user_id(db, saved_project.owner)

    project_members = []
    for project_user in saved_project.members:
        found_user = find_user_by_user_id(db, project_user.user_id)
        project_member = ProjectUserRes.from_user(found_user, project_user.role)
        project_members.append(project_member)

    project_res = ProjectRes.from_project(saved_project, owner_user, project_members)

    return project_res


def delete_project(user_id: int, project_id: int, db: Session):
    """
    Delete the existing project by project id
    """
    existing_project = repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    if existing_project.owner == int(user_id):
        repository.delete_project(db, existing_project)
    else:
        raise ProjectOwnerMismatched()


async def upload_file(project_name: str, files: List[UploadFile]):
    """
    Upload design documents to the project directory
    """
    if not files:
        return []

    project_dir = os.path.join("design_docs", project_name)
    os.makedirs(project_dir, exist_ok=True)

    uploaded_paths = []
    for file in files:
        safe_filename = file.filename.replace("/", "_").replace("\\", "_")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        saved_filename = f"{timestamp}_{safe_filename}"
        file_path = os.path.join(project_dir, saved_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_paths.append(file_path)

    return uploaded_paths


async def list_files_in_directory(project_name: str):
    """
    List all files in the given directory
    """

    project_dir = os.path.join("design_docs", project_name)
    try:
        files = os.listdir(project_dir)
        # parse the file names to get the original file names
        files = [file.split("_", 1)[-1] for file in files]
        return files
    except FileNotFoundError:
        raise FileNotFoundError


async def delete_file(file_path: str):
    """
    Delete a file from the given path
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False
    except Exception as e:
        raise FileDeleteError()
