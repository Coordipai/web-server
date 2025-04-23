from typing import List
from fastapi import File, HTTPException, Path, UploadFile
from sqlalchemy.orm import Session
import aiofiles

from src.models import Project
from project.schemas import ProjectReq, ProjectRes
from project import repository
from src.exceptions.definitions import ProjectAlreadyExist


async def create_project(project_req: ProjectReq, files: List[UploadFile], db: Session):
    """
    Create a new project

    Returns project data
    """
    existing_project = repository.find_project_by_name(db, project_req.project_name)

    if existing_project:
        raise ProjectAlreadyExist()

    project = Project(
        project_name=project_req.project_name,
        repo_name=project_req.repo_name,
        start_date=project_req.start_date,
        end_date=project_req.end_date,
        sprint_unit=project_req.sprint_unit,
        discord_channel_id=project_req.discord_chnnel_id,
    )

    saved_project = repository.create_project(db, project)
    project_res = ProjectRes.model_validate(saved_project)

    # TODO Embedding project files
    # saved_files = await upload_file(saved_project.project_name, files)

    return project_res


def get_project(project_id: int, db: Session):
    return


def update_project(
    project_id: int, project_req: ProjectReq, files: List[UploadFile], db: Session
):
    return


def delete_project(project_id: int, db: Session):
    return


async def upload_file(project_name: str, files: List[UploadFile]):
    for file in files:
        safe_filename = file.filename.replace("/", "_")
        print(safe_filename)
