import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.agent import agent, aprompt, chain
from src.agent.schemas import (
    AssessStatRes,
    FeedbackReq,
    FeedbackRes,
    GenerateIssueListRes,
    RecommendAssigneeListRes,
    RecommendAssigneeReq,
)
from src.config.database import get_db
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    assess_success,
    feedback_success,
    issue_assign_success,
)

router = APIRouter(prefix="/agent", tags=["Agent"])

# ───────────────────────────────────────────────────────────────────────────────────────
#                                ## Generate Issues ##
# ───────────────────────────────────────────────────────────────────────────────────────
@router.get(
    "/generate_issues/{project_id}",
    summary="Generate issues",
    response_model=GenerateIssueListRes,
)
async def generate_issues(project_id: int, db: Session = Depends(get_db)):
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    return StreamingResponse(
        executor.generate_issues(project_id, db),
        media_type="application/json",
    )


@router.post(
    "/generate_issues_test",
)
async def generate_issues_test(project_id: int):
    """
    Test the agent functionality.
    """
    print("Agent test started")
    agent_generating_issues = agent.agent
    print("Agent initialized")
    result = await agent_generating_issues.ainvoke(aprompt.generate_issue_template.format(
        project_id=project_id,
        feature_example=aprompt.feature_example
    ))
    print("Agent invoked")
    return json.loads(result.get("output"))


# ───────────────────────────────────────────────────────────────────────────────────
#                                  ## Assess Stat ##
# ───────────────────────────────────────────────────────────────────────────────────
@router.post(
    "/assess_stat", 
    summary="Assess Stat", 
    response_model=SuccessResponse[AssessStatRes]
)
async def assess_stat(
    request: Request, db: Session = Depends(get_db)
):
    """
    Assess the competency of a user based on their GitHub activity.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.assess_competency(
        request.state.user_id, db
    )

    return assess_success(result)


@router.post(
    "/assess_stat_test",
)
async def assess_stat_test():
    """
    Test the assess stat functionality.
    """
    print("Assess stat test started")
    agent_assessing_stat = agent.agent
    print("Agent initialized")
    result = await agent_assessing_stat.ainvoke(aprompt.assess_stat_template.format(
        user_id=1,
    ))

    print("Agent invoked")
    return json.loads(result.get("output"))


# ───────────────────────────────────────────────────────────────────────────────────────────
#                              ## Recommend Assignees ##
# ───────────────────────────────────────────────────────────────────────────────────────────
@router.post(
    "/recommend_assignees/{project_id}",
    summary="Recommend assignees for issues",
    response_model=SuccessResponse[RecommendAssigneeListRes],
)
async def recommend_assignees(
    project_id: int, recommendAssigneeReq: RecommendAssigneeReq, db: Session = Depends(get_db)
):
    """
    Recommend assignees for issues based on their competency.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.recommend_assignees_for_issues(
        db, project_id, recommendAssigneeReq.issues
    )

    return issue_assign_success(result)


@router.post(
    "/recommend_assignees_test",
)
async def recommend_assignees_test(project_id: int):
    """
    Test the issue assignment functionality.
    """
    print("Issue assignment test started")
    agent_assigning_issues = agent.agent
    print("Agent initialized")
    result = await agent_assigning_issues.ainvoke(aprompt.recommend_assignee_template.format(
        project_id=project_id,
        issues=aprompt.made_issue_example
    ))
    print("Agent invoked")
    return json.loads(result.get("output"))


# ────────────────────────────────────────────────────────────────────────────────────
#                                  ## Get Feedback ##
# ────────────────────────────────────────────────────────────────────────────────────
@router.get(
    "/feedback",
    summary="Get feedback for issue rescheduling",
    response_model=SuccessResponse[FeedbackRes],
)
async def get_feedback(feedbackReq: FeedbackReq, db: Session = Depends(get_db)):
    """
    Get feedback for issue rescheduling.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.get_feedback(feedbackReq.project_id, feedbackReq.issue_rescheduling_id, db)

    return feedback_success(result)


@router.post(
    "/get_feedback_test",
)
async def get_feedback_test(feedbackReq: FeedbackReq):
    """
    Test the issue rescheduling functionality.
    """
    print("Issue rescheduling test started")
    agent_rescheduling_issues = agent.agent
    print("Agent initialized")
    result = await agent_rescheduling_issues.ainvoke(aprompt.issue_rescheduling_template.format(
        project_id=1,
        issue_rescheduling_id=feedbackReq.issue_rescheduling_id,  
    ))
    print("Agent invoked")
    return json.loads(result.get("output"))

