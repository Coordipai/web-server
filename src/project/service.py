from typing import List, Optional
from fastapi import File, UploadFile
from sqlalchemy.orm import Session

from src.models import Project
from project.schemas import ProjectReq, ProjectRes
from project import repository
from src.exceptions.definitions import ProjectAlreadyExist, ProjectNotFound
from src.user.repository import find_user_by_user_id
from src.user.schemas import UserRes


def create_project(
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

    project = Project(
        name=project_req.name,
        owner=user_id,
        repo_name=project_req.repo_name,
        start_date=project_req.start_date,
        end_date=project_req.end_date,
        sprint_unit=project_req.sprint_unit,
        discord_channel_id=project_req.discord_chnnel_id,
    )

    saved_project = repository.create_project(db, project)
    owner_user = find_user_by_user_id(db, user_id)
    print(owner_user)
    project_res = ProjectRes(
        id=saved_project.id,
        name=saved_project.name,
        owner=UserRes.model_validate(owner_user),
        repo_name=saved_project.repo_name,
        start_date=saved_project.start_date,
        end_date=saved_project.end_date,
        sprint_unit=saved_project.sprint_unit,
        discord_channel_id=saved_project.discord_channel_id,
    )

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

    project_res = ProjectRes.model_validate(existing_project)

    return project_res


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
    existing_project.repo_name = (project_req.repo_name,)
    existing_project.start_date = (project_req.start_date,)
    existing_project.end_date = (project_req.end_date,)
    existing_project.sprint_unit = (project_req.sprint_unit,)
    existing_project.discord_channel_id = (project_req.discord_chnnel_id,)

    saved_project = repository.update_project(db, existing_project)
    project_res = ProjectRes.model_validate(saved_project)

    # TODO Embedding project files
    # saved_files = await upload_file(saved_project.project_name, files)

    return project_res


def delete_project(project_id: int, db: Session):
    """
    Delete the existing project by project id
    """
    existing_project = repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    repository.delete_project(db, existing_project)


async def upload_file(project_name: str, files: List[UploadFile]):
    for file in files:
        safe_filename = file.filename.replace("/", "_")
        print(safe_filename)
