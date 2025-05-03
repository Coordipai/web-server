
from fastapi import APIRouter
from src.agent import chain
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    issue_generate_success
)

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.get(
        "/generate_issues",
        summary="Generate issues",
        response_model=SuccessResponse[list]
        )
async def generate_issues():
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    result = await executor.generate_issues()

    return issue_generate_success(result)
