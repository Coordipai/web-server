from src.agent import tool
from src.user import repository as user_repository
from fastapi.datastructures import UploadFile as FastUploadFile
from pathlib import Path
from sqlalchemy.orm import Session


class CustomAgentExecutor:
    def __init__(self):
        pass

    async def generate_issues(self) -> dict:
        """
        Generate issues using the agent executor.
        """
        
        # TODO: Get documents and issue template from database

        # Load documents with file path (pdf, docx)
        test_file_path = Path("/your_path/web-server/test_docs.pdf")
        with open(test_file_path, "rb") as f:
            upload_file = FastUploadFile(filename=test_file_path.name, file=f)
            text = await tool.extract_text_from_documents(upload_file)

        features = await tool.define_features(text)
        issues = await tool.make_issues(text, features)

        return issues
    
    async def assess_competency(self, user_id: str, db: Session) -> dict:
        """
        Assess the competency of a user based on their GitHub activity.
        """

        # get user
        user = user_repository.find_user_by_user_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        activity_info = await tool.get_github_activation_info(user.github_access_token)
        if not activity_info:
            raise ValueError("Failed to retrieve GitHub activity information")
        
        stat = await tool.assess_with_data(user, activity_info)
        
        user.stat = stat
        db.commit()
        db.refresh(user)

        return user.stat


