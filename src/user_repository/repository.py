from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import UserRepository
from src.response.error_definitions import SQLError

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def sync_user_repositories(db: Session, user_id: int, repo_names: list[str]) -> None:
    try:
        # Get saved repositories
        existing_repos = (
            db.query(UserRepository).filter(UserRepository.user_id == user_id).all()
        )
        existing_repo_names = {repo.repo_fullname for repo in existing_repos}

        # Incoming repository names
        new_repo_names = set(repo_names)

        # Existed but not in new request
        to_delete = [
            repo for repo in existing_repos if repo.repo_fullname not in new_repo_names
        ]
        for repo in to_delete:
            db.delete(repo)

        # New request has it, but existing one doesn't
        to_add = new_repo_names - existing_repo_names
        for repo_name in to_add:
            new_repo = UserRepository(user_id=user_id, repo_fullname=repo_name)
            db.add(new_repo)

        db.commit()

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError(detail=str(e))


def find_all_repositories_by_user_id(db: Session, user_id: int) -> UserRepository:
    try:
        repos = db.query(UserRepository).filter(UserRepository.user_id == user_id).all()
        return repos
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError(detail=str(e))
