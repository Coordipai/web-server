import json
import os
from pathlib import Path

from fastapi.datastructures import UploadFile as FastUploadFile
from sqlalchemy.orm import Session

from src.agent import tool
from src.agent.schemas import (
    AssessStatRes,
    AssignedIssueListRes,
    AssignedIssueRes,
    FeedbackRes,
    GenerateIssueListRes,
    GenerateIssueRes,
)
from src.issue import repository as issue_repository
from src.issue_rescheduling import repository as issue_rescheduling_repository
from src.project import repository as project_repository
from src.response.error_definitions import (
    DesignDocNotFound,
    GitHubActivationInfoError,
    IssueNotFound,
    IssueReschedulingNotFound,
    ProjectNotFound,
    UserNotFound,
)
from src.user import repository as user_repository
from src.user_repository import service as user_repository_service


class CustomAgentExecutor:
    def __init__(self):
        pass

    async def generate_issues(self, project_id: int, db: Session):
        """
        Generate issues using the agent executor.
        """
        print("--------------------------------------------")
        print("Starting issue generation...")
        print("--------------------------------------------")

        # Get project information   
        project = project_repository.find_project_by_id(db, project_id)
        if not project:
            raise ProjectNotFound()
        
        project_dir = os.path.join("design_docs", project.name)
        file_names = os.listdir(project_dir)
        if not file_names:
            raise DesignDocNotFound()
        
        files = [os.path.join(project_dir, file_name) for file_name in file_names]

        extracted_texts = ""
        for file in files:
            # Load documents with file path (pdf, docx)
            file_path = Path(file)
            with open(file_path, "rb") as f:
                upload_file = FastUploadFile(filename=file_path.name, file=f)
                text = await tool.extract_text_from_documents(upload_file)
                extracted_texts += file_path.name
                extracted_texts += "\n"
                extracted_texts += text
                extracted_texts += "\n\n"

        features = await tool.define_features(extracted_texts)
        async for issue in tool.make_issues(extracted_texts, features):
            issueRes = GenerateIssueRes(
                type=issue["type"],
                name=issue["name"],
                description=issue["description"],
                title=issue["title"],
                labels=issue["labels"],
                body=issue["body"]
            )
            yield json.dumps(dict(issueRes), ensure_ascii=False, indent=4)

        print("--------------------------------------------")
        print("Issues generated successfully.")
        print("--------------------------------------------")
    

    async def assess_competency(self, user_id: int, db: Session):
        """
        Assess the competency of a user based on their GitHub activity.
        """

        print("Starting competency assessment...")

        # get user
        user = user_repository.find_user_by_user_id(db, user_id)
        if not user:
            raise UserNotFound()
        
        selected_repo_names = user_repository_service.get_all_selected_repositories(user_id, db)
        activity_info = await tool.get_github_activation_info(selected_repo_names, user.github_access_token)
        if not activity_info:
            raise GitHubActivationInfoError()
        
        stat = await tool.assess_with_data(user, activity_info)
        user_repository.update_user_stat(db, user, stat)

        print("--------------------------------------------")
        print("Competency assessment completed.")
        print("--------------------------------------------")

        return AssessStatRes(
            name=stat["Name"],
            field=stat["Field"],
            experience=stat["Experience"],
            evaluation_scores=stat["evaluation_scores"],
            implemented_features=stat["implemented_features"]
        )
    

    async def assign_issue_to_users(self, db: Session, project_id: str, user_ids: list[str], issues: GenerateIssueListRes):
        """
        Assign issues to users.
        """

        print("--------------------------------------------")
        print("Starting issue assignment...")
        print("--------------------------------------------")

        # Get project information from database
        project = project_repository.find_project_by_id(db, project_id)
        if not project:
            raise ProjectNotFound()

        # Get user stat from database
        user_stat_list = list()
        for user_id in user_ids:
            user = user_repository.find_user_by_user_id(db, user_id)
            if not user:
                raise UserNotFound()
            user_stat_list.append(user.stat)

        # Assign issues to users
        assigned_issues = await tool.assign_issues_to_users("project", user_stat_list, issues)

        assigned_issue_list_res = list()
        for issue in assigned_issues:
            assigned_issue_res = AssignedIssueRes(
                issue=issue["issue"],
                assignee=issue["assignee"],
                description=issue["description"]
            )
            assigned_issue_list_res.append(assigned_issue_res)

        print("--------------------------------------------")
        print("Issue assignment completed.")
        print("--------------------------------------------")
            
        return AssignedIssueListRes(issues=assigned_issue_list_res)


    async def get_feedback(self, project_id: int, issue_rescheduling_id: int, db: Session):
        """
        Get feedback for issue rescheduling.
        """

        print("--------------------------------------------")
        print("Starting feedback generation...")
        print("--------------------------------------------")

        # Get project information from database
        project = project_repository.find_project_by_id(db, project_id)
        if not project:
            raise ProjectNotFound()

        # Get issue rescheduling information from database
        issue_rescheduling = issue_rescheduling_repository.find_issue_scheduling_by_id(db, issue_rescheduling_id)
        if not issue_rescheduling:
            raise IssueReschedulingNotFound()
        
        # Get user stat from database
        members = project.members
        user_stat_list = list()
        for member in members:
            user = user_repository.find_user_by_user_id(db, member.user_id)
            if not user:
                raise UserNotFound()
            user_stat_list.append(user.stat)

        # Get issue information from database
        issue = issue_repository.find_issue_by_issue_number(
            project.owner, project.repo_fullname, issue_rescheduling.issue_number, db
        )
        if not issue:
            raise IssueNotFound

        feedback = await tool.get_feedback(project, user_stat_list, issue_rescheduling, issue)

        print("--------------------------------------------")
        print("Feedback generation completed.")
        print("--------------------------------------------")
        
        return FeedbackRes(
            suggested_assignees=feedback['suggestions']["new_assignee"]["name"],
            suggested_sprints=feedback['suggestions']["new_sprint"]["sprint"],
            reason_for_assignees=feedback['suggestions']["new_assignee"]["reason"],
            reason_for_sprints=feedback['suggestions']["new_sprint"]["reason"]
        )
