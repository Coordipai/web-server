from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import Project, ProjectUser
from src.response.error_definitions import SQLError

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def create_project(
    db: Session, project: Project, members: List[ProjectUser]
) -> Project:
    try:
        # Create project
        db.add(project)
        db.flush()

        # Create project user
        for member in members:
            member.project_id = project.id
            db.add(member)

        db.commit()
        return project
    except SQLAlchemyError as e:
        logger.error(f"Database error during project creation: {e}")
        raise SQLError()


def find_project_by_id(db: Session, project_id: int) -> Project | None:
    try:
        result = db.execute(select(Project).filter(Project.id == project_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_project_by_name(db: Session, project_name: str) -> Project | None:
    try:
        result = db.execute(select(Project).filter(Project.name == project_name))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_project_by_discord_channel_id(
    db: Session, discord_channel_id: str
) -> Project | None:
    try:
        result = db.execute(
            select(Project).filter(Project.discord_channel_id == discord_channel_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_project_by_owner(db: Session, owner: str) -> list[Project]:
    try:
        result = db.execute(select(Project).filter(Project.owner == owner))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_all_active_projects(db: Session) -> List[Project]:
    try:
        current_time = datetime.now(timezone.utc)
        result = db.execute(
            select(Project)
            .filter(Project.end_date > current_time)
            .order_by(Project.end_date.asc())
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error during active projects retrieval: {e}")
        db.rollback()
        raise SQLError()


def update_project(
    db: Session, project: Project, members: List[ProjectUser]
) -> Project:
    try:
        # Remove old project members
        db.query(ProjectUser).filter(ProjectUser.project_id == project.id).delete()

        # Update project
        db.add(project)
        db.flush()

        # Create new project members
        for member in members:
            member.project_id = project.id
            db.add(member)

        db.commit()
        return project
    except SQLAlchemyError as e:
        logger.error(f"Database error during project creation: {e}")
        db.rollback()
        raise SQLError()


def delete_project(db: Session, project: Project):
    try:
        db.delete(project)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_projects_by_member(db: Session, user_id: int) -> list[Project]:
    try:
        result = db.execute(
            select(Project).join(Project.members).filter(ProjectUser.user_id == user_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error during member projects retrieval: {e}")
        db.rollback()
        raise SQLError()
