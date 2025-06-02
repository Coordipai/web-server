import os
import shutil
from typing import List, Optional

from fastapi import File, UploadFile
from sqlalchemy.orm import Session

from project.schemas import ProjectListRes, ProjectReq, ProjectRes
from src.common.util.github import check_github_repo_exists
from src.models import Project, ProjectUser
from src.project import repository as project_repository
from src.project_user import repository as project_user_repository
from src.response.error_definitions import (
    FileDeleteError,
    ProjectAlreadyExist,
    ProjectNotFound,
    ProjectOwnerMismatched,
    ProjectPermissionDenied,
    RepositoryNotFoundInGitHub,
    UserNotFound,
)
from src.user.repository import find_user_by_user_id


def create_project(
    user_id: int,
    project_req: ProjectReq,
    db: Session,
    files: Optional[List[UploadFile]] = File(None),
) -> ProjectRes:
    """
    Create new project
    """
    existing_project = project_repository.find_project_by_name(db, project_req.name)
    if existing_project:
        raise ProjectAlreadyExist()

    design_doc_paths = upload_file(project_req.name, files)

    is_repo = check_github_repo_exists(user_id, project_req.repo_fullname, db)
    if not is_repo:
        raise RepositoryNotFoundInGitHub(project_req.repo_fullname)

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

    members = []
    for member_req in project_req.members:
        found_user = find_user_by_user_id(db, member_req.id)
        if not found_user:
            raise UserNotFound()

        project_user = ProjectUser(user_id=found_user.id, role=member_req.role)
        members.append(project_user)

    saved_project = project_repository.create_project(db, project, members)

    owner_user = find_user_by_user_id(db, user_id)
    if not owner_user:
        raise UserNotFound()

    return ProjectRes.from_project(saved_project, owner_user, design_doc_paths)


def get_all_projects(user_id: int, db: Session) -> List[ProjectListRes]:
    """
    Get all existing projects that user owns or participates in
    """
    owned_projects = project_repository.find_project_by_owner(db, user_id)
    participated_projects = project_user_repository.find_all_projects_by_user_id(
        db, user_id
    )

    project_list = []
    added_project_ids = set()

    for project in owned_projects:
        is_repo = check_github_repo_exists(user_id, project.repo_fullname, db)
        if not is_repo:
            raise RepositoryNotFoundInGitHub(project.repo_fullname)

        if project.id not in added_project_ids:
            project_list.append(ProjectListRes.model_validate(project))
            added_project_ids.add(project.id)

    for project_user in participated_projects:
        project = project_repository.find_project_by_id(db, project_user.project_id)

        is_repo = check_github_repo_exists(user_id, project.repo_fullname, db)
        if not is_repo:
            raise RepositoryNotFoundInGitHub(project.repo_fullname)

        if project.id not in added_project_ids:
            project_list.append(ProjectListRes.model_validate(project))
            added_project_ids.add(project.id)

    return project_list


def get_project(user_id: int, project_id: int, db: Session) -> ProjectRes:
    """
    Get the existing project by project id
    """
    existing_project = project_repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    is_repo = check_github_repo_exists(user_id, existing_project.repo_fullname, db)
    if not is_repo:
        raise RepositoryNotFoundInGitHub(existing_project.repo_fullname)

    owner_user = find_user_by_user_id(db, existing_project.owner)
    if not owner_user:
        raise UserNotFound()

    design_docs = list_files_in_directory(existing_project.name)

    return ProjectRes.from_project(existing_project, owner_user, design_docs)


def update_project(
    user_id: int,
    project_id: int,
    project_req: ProjectReq,
    files: List[UploadFile],
    db: Session,
):
    """
    Update the existing project by project id
    """
    existing_project = project_repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    is_owner = existing_project.owner == user_id
    is_member = project_repository.is_project_member(db, project_id, user_id)

    if not (is_owner or is_member):
        raise ProjectPermissionDenied()

    is_repo = check_github_repo_exists(user_id, existing_project.repo_fullname, db)
    if not is_repo:
        raise RepositoryNotFoundInGitHub(existing_project.repo_fullname)

    updated_design_doc_paths = update_file(
        existing_project.name, files, project_req.design_docs
    )

    if existing_project.name != project_req.name:
        existing_project.name = project_req.name
        # Update the directory name to match the new project name
        new_project_dir = os.path.join("design_docs", project_req.name)
        old_project_dir = os.path.join("design_docs", existing_project.name)
        os.rename(old_project_dir, new_project_dir)

    existing_project.repo_fullname = (project_req.repo_fullname,)
    existing_project.start_date = (project_req.start_date,)
    existing_project.end_date = (project_req.end_date,)
    existing_project.sprint_unit = (project_req.sprint_unit,)
    existing_project.discord_channel_id = (project_req.discord_channel_id,)
    existing_project.design_doc_paths = updated_design_doc_paths

    members = []
    for member_req in project_req.members:
        found_user = find_user_by_user_id(db, member_req.id)
        if not found_user:
            raise UserNotFound()

        project_user = ProjectUser(user_id=found_user.id, role=member_req.role)
        members.append(project_user)

    saved_project = project_repository.update_project(db, existing_project, members)

    owner_user = find_user_by_user_id(db, saved_project.owner)
    if not owner_user:
        raise UserNotFound()

    return ProjectRes.from_project(saved_project, owner_user, updated_design_doc_paths)


def delete_project(user_id: int, project_id: int, db: Session):
    """
    Delete the existing project by project id
    """
    existing_project = project_repository.find_project_by_id(db, project_id)

    if not existing_project:
        raise ProjectNotFound()

    if existing_project.owner == int(user_id):
        delete_file(os.path.join("design_docs", existing_project.name))
        project_repository.delete_project(db, existing_project)
    else:
        raise ProjectOwnerMismatched()


def upload_file(project_name: str, files: List[UploadFile]):
    """
    Upload design documents to the project directory
    """
    project_dir = os.path.join("design_docs", project_name)
    os.makedirs(project_dir, exist_ok=True)

    if not files:
        return []

    existing_files = set(os.listdir(project_dir))

    for file in files:
        safe_filename = file.filename.replace("/", "_").replace("\\", "_")
        if safe_filename in existing_files:  # check if file already exists
            continue
        file_path = os.path.join(project_dir, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    uploaded_paths = list_files_in_directory(project_name)

    return uploaded_paths


def list_files_in_directory(project_name: str):
    """
    List all files in the given directory
    """

    project_dir = os.path.join("design_docs", project_name)
    try:
        files = os.listdir(project_dir)
        return files
    except FileNotFoundError:
        raise FileNotFoundError


def update_file(
    project_name: str, files: List[UploadFile], updated_file_names: List[str] = []
):
    """
    Update a file in the given directory
    """
    existing_files = set(list_files_in_directory(project_name))
    updated_files = set(updated_file_names)
    files_to_delete = existing_files - updated_files

    for file_name in files_to_delete:
        file_path = os.path.join("design_docs", project_name, file_name)
        delete_file(file_path)

    if not files:
        return list_files_in_directory(project_name)

    updated_paths = upload_file(project_name, files)

    return updated_paths


def delete_file(file_path: str):
    """
    Delete a path or file from the given path
    """
    try:
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
            return True
        elif os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False
    except Exception as e:
        raise FileDeleteError()
