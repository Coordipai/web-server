from datetime import datetime
import json
from typing import List, Optional
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.exceptions.definitions import InvalidJsonDataFormat, InvalidJsonFormat
from src.project.schemas import ProjectReq
from project import service

router = APIRouter(prefix="/project", tags=["Project"])


@router.post("/", summary="Create a new project")
def create_project(
    request: Request,
    project_req: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    return service.create_project(
        user_id, parse_project_req_str(project_req), db, files
    )


@router.get("/{project_id}", summary="Get existing project")
def get_project(project_id: int, db: Session = Depends(get_db)):
    return service.get_project(project_id, db)


@router.put("/{project_id}", summary="Update existing project")
def update_project(
    project_id: int,
    project_req: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    return service.update_project(
        project_id, parse_project_req_str(project_req), files, db
    )


@router.delete("/{project_id}", summary="Delete existing project")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    return service.delete_project(project_id, db)


def parse_project_req_str(project_req: str = Form(...)):
    try:
        project_req_data = json.loads(project_req)
        project_req_data["start_date"] = datetime.fromisoformat(
            project_req_data["start_date"].replace("Z", "+00:00")
        )
        project_req_data["end_date"] = datetime.fromisoformat(
            project_req_data["end_date"].replace("Z", "+00:00")
        )
        project_req_obj = ProjectReq(**project_req_data)
        return project_req_obj
    except json.JSONDecodeError:
        raise InvalidJsonFormat()
    except ValueError as e:
        raise InvalidJsonDataFormat()
