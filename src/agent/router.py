
from fastapi import APIRouter
from src.agent import chain

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.get(
        "/generate_issues",
        summary="Generate issues")
async def generate_issues():
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    result = await executor.generate_issues()
    return result
