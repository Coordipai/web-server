from pathlib import Path

from fastapi.datastructures import UploadFile as FastUploadFile
from sqlalchemy.orm import Session

from src.agent import tool
from src.agent.schemas import (
    AssessStatRes,
    AssignedIssueListRes,
    AssignedIssueRes,
    GenerateIssueListRes,
    GenerateIssueRes,
)
from src.project import repository as project_repository
from src.response.error_definitions import (
    GitHubActivationInfoError,
    ProjectNotFound,
    UserNotFound,
)
from src.user import repository as user_repository


class CustomAgentExecutor:
    def __init__(self):
        pass

    async def generate_issues(self):
        """
        Generate issues using the agent executor.
        """
        
        # TODO: Get documents and issue template from database

        # Load documents with file path (pdf, docx)
        test_file_path = Path("/Users/junhyung85920/Desktop/KNU/25-1/종합설계프로젝트1/web-server/test_docs.pdf")
        with open(test_file_path, "rb") as f:
            upload_file = FastUploadFile(filename=test_file_path.name, file=f)
            text = await tool.extract_text_from_documents(upload_file)

        features = await tool.define_features(text)
        issues = await tool.make_issues(text, features)

        # for each issue into IssueRes
        issueResList = list()
        for issue in issues:
            issueRes = GenerateIssueRes(
                type=issue["type"],
                name=issue["name"],
                description=issue["description"],
                title=issue["title"],
                labels=issue["labels"],
                body=issue["body"]
            )
            issueResList.append(issueRes)
            

        return GenerateIssueListRes(issues=issueResList)
    

    async def assess_competency(self, user_id: int, selected_repos: list[str], db: Session):
        """
        Assess the competency of a user based on their GitHub activity.
        """

        # get user
        user = user_repository.find_user_by_user_id(db, user_id)
        if not user:
            raise UserNotFound()
        
        activity_info = await tool.get_github_activation_info(user.github_access_token)
        if not activity_info:
            raise GitHubActivationInfoError()
        
        stat = await tool.assess_with_data(user, activity_info)
        user_repository.update_user_stat(db, user, stat)

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
            
        return AssignedIssueListRes(issues=assigned_issue_list_res)



