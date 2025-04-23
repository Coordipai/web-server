from datetime import datetime
import json
from typing import List
from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi import Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.exceptions.definitions import InvalidJsonDataFormat, InvalidJsonFormat
from src.project.schemas import ProjectReq
from project import service

router = APIRouter(prefix="/project", tags=["Project"])


@router.post("/", summary="Create a new project")
async def create_project(
    project_req: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    try:
        project_req_data = json.loads(project_req)
        project_req_data["start_date"] = datetime.fromisoformat(
            project_req_data["start_date"].replace("Z", "+00:00")
        )
        project_req_data["end_date"] = datetime.fromisoformat(
            project_req_data["end_date"].replace("Z", "+00:00")
        )
        project_req_obj = ProjectReq(**project_req_data)
    except json.JSONDecodeError:
        raise InvalidJsonFormat()
    except ValueError as e:
        raise InvalidJsonDataFormat()

    return await service.create_project(project_req_obj, files, db)


@router.get("/{project_id}", summary="Get existing project")
def get_project(project_id: int, db: Session = Depends(get_db)):
    return service.read_project(project_id, db)


@router.put("/{project_id}", summary="Update existing project")
def update_project(
    project_id: int,
    project_req: ProjectReq = Body(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    return service.create_project(project_id, project_req, files, db)


@router.delete("/{id}", summary="Delete existing project")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    return service.create_project(project_id, db)
