from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from src.project.models import Project
from src.user.models import User
from src.user.schemas import UserCategory, UserRes


class ProjectUserReq(BaseModel):
    id: int
    role: str


class ProjectUserRes(BaseModel):
    id: int
    name: str
    github_id: int
    github_name: str
    category: UserCategory
    role: str
    profile_img: str

    @classmethod
    def from_user(cls, user: User, role: str) -> "ProjectUserRes":
        return cls(
            id=user.id,
            name=user.name,
            github_id=user.github_id,
            github_name=user.github_name,
            category=user.category,
            role=role,
            profile_img=user.profile_img,
        )


class ProjectReq(BaseModel):
    name: str
    repo_fullname: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int
    discord_channel_id: str
    members: List[ProjectUserReq]
    design_docs: List[str] = []


class ProjectRes(BaseModel):
    id: int
    name: str
    owner: UserRes
    repo_fullname: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int
    discord_channel_id: str
    members: List[ProjectUserRes]
    design_docs: List[str]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_project(
        cls,
        project: Project,
        owner: User,
        design_docs: List[str] = [],
    ) -> "ProjectRes":
        return cls(
            id=project.id,
            name=project.name,
            owner=UserRes.model_validate(owner),
            repo_fullname=project.repo_fullname,
            start_date=project.start_date,
            end_date=project.end_date,
            sprint_unit=project.sprint_unit,
            discord_channel_id=project.discord_channel_id,
            members=[
                ProjectUserRes.from_user(member.user, member.role)
                for member in project.members
            ],
            design_docs=design_docs,
        )


class ProjectListRes(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int

    model_config = ConfigDict(from_attributes=True)
