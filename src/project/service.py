from typing import List, Optional
from fastapi import File, UploadFile
from sqlalchemy.orm import Session

from src.models import Project, ProjectUser
from project.schemas import ProjectReq, ProjectRes, ProjectUserRes
from project import repository
from src.response.error_definitions import (
    ProjectAlreadyExist,
    ProjectNotFound,
    ProjectOwnerMismatched,
)

from src.project_user.repository import create_project_user
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
        repo_fullname=project_req.repo_fullname,
        start_date=project_req.start_date,
        end_date=project_req.end_date,
        sprint_unit=project_req.sprint_unit,
        discord_channel_id=project_req.discord_chnnel_id,
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
    project_res = ProjectRes.from_project(saved_project, owner_user, project_members)

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

    project_res = ProjectRes.from_project(existing_project, owner_user, project_members)

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
    existing_project.repo_fullname = (project_req.repo_fullname,)
    existing_project.start_date = (project_req.start_date,)
    existing_project.end_date = (project_req.end_date,)
    existing_project.sprint_unit = (project_req.sprint_unit,)
    existing_project.discord_channel_id = (project_req.discord_chnnel_id,)

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
    for file in files:
        safe_filename = file.filename.replace("/", "_")
        print(safe_filename)
