import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from project import service
from src.config.database import get_db
from src.project.schemas import ProjectReq, ProjectRes
from src.response.error_definitions import InvalidJsonDataFormat, InvalidJsonFormat
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    project_create_success,
    project_delete_success,
    project_read_success,
    project_update_success,
)

router = APIRouter(prefix="/project", tags=["Project"])


@router.post(
    "/",
    summary="Create a new project",
    response_model=SuccessResponse[ProjectRes],
)
def create_project(
    request: Request,
    project_req: str = Form(
        ...,
        description=(
            "JSON string matching the ProjectReq schema.\n\n"
            "example:\n\n"
            "{\n\n"
            '  "name": "My Project",\n\n'
            '  "repo_fullname": "my-repo",\n\n'
            '  "start_date": "2025-01-01T00:00:00Z",\n\n'
            '  "end_date": "2025-03-01T00:00:00Z",\n\n'
            '  "sprint_unit": 2,\n\n'
            '  "discord_chnnel_id": 1234567890,\n\n'
            '  "members": [\n\n'
            '   {"id": 1, "role": "backend"},\n\n'
            '   {"id": 2, "role": "frontend"}\n\n'
            "  ]\n\n"
            "}"
        ),
    ),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    data = service.create_project(
        user_id, parse_project_req_str(project_req), db, files
    )
    return project_create_success(data)


@router.get(
    "/{project_id}",
    summary="Get existing project",
    response_model=SuccessResponse[ProjectRes],
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    data = service.get_project(project_id, db)
    return project_read_success(data)


@router.put(
    "/{project_id}",
    summary="Update existing project",
    response_model=SuccessResponse[ProjectRes],
)
def update_project(
    project_id: int,
    project_req: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    data = service.update_project(
        project_id, parse_project_req_str(project_req), files, db
    )
    return project_update_success(data)


@router.delete(
    "/{project_id}",
    summary="Delete existing project",
    response_model=SuccessResponse,
)
def delete_project(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    service.delete_project(user_id, project_id, db)
    return project_delete_success()


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
