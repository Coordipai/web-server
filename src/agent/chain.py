from src.agent import tool
from fastapi.datastructures import UploadFile as FastUploadFile
from pathlib import Path


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
