from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools.render import render_text_description


define_feature_template = PromptTemplate(
    input_variables=["example", "documents"],
    template=(
        "Analyze the planning/design documents.\n"
        "Break down and define the development tasks needed to complete the project.\n"
        "Divide the tasks such that each task can be completed within one hour.\n"
        "List the divided tasks in order of development sequence.\n"
        "Each task should be written in task name\n"
        "Define necessary tasks for the project.\n"
        "The output should be a list of task names in json.\n\n"

        "Output example: {example}"

        "Planning/Design Documents: {documents}\n\n"

    )
)

make_issue_template = PromptTemplate(
    input_variables=["documents", "issue_template", "features"],
    template=(
        "Analyze the planning/design documents.\n"
        "Write the implementation steps for each feature.\n"
        "Write any additional information and reference materials required to implement each feature.\n"
        "Write the criteria for the personnel required for each feature in terms of scores, based on the score table.\n"
        "Each task should be written according to the issue template.\n"
        "All contents in the issue template should be written in Korean.\n"
        "Name(right of ':'), description on the top in the issue template should be written in Korean.\n"
        
        "Make only one issue per each issue name.\n"
        "The output should be a list of complete tasks in json.\n\n"

        "Planning/Design Documents: {documents}\n\n"
        "Issue template with Example Value: {issue_template}\n\n"
        "Issue names: {features}"
    )
)


docs = """
- Common
    1. 로그인
        1. `User → Web UI` 로그인 버튼 클릭
        2. `Web UI → Web Server` 로그인 요청
        3. `Web Server → Github` 액세스 토큰 요청 및 반환
        4. `Web Server → Github` 유저 역량 정보 요청 및 반환
        5. `Web Server → Embedding Model` 역량 정보 임베딩 요청 및 반환
        6. `Web Server → Vector DB` 임베딩된 자료 저장
        7. `Web Server → Github` 유저 정보 저장
    2. 역량 정보 제출
        1. `User → Web UI` 역량 정보 요청
        2. `Web UI → Web Server` 역량 정보 요청
        3. `Web Server → Github` 액세스 토큰 요청 및 반환
        4. `Web Server → Github` 유저 역량 정보 요청 및 반환
        5. `Web Server → Embedding Model` 역량 정보 임베딩 요청 및 반환
        6. `Web Server → Vector DB` 임베딩된 자료 저장
        7. `Web Server → RDB` 유저 정보 저장
- Admin
    1. 프로젝트 생성
        1. `Admin → Web UI` 프로젝트 생성 버튼 클릭
        2. `Web UI → Web Server` 프로젝트 생성 요청
        3. `Web Server → Agent` 프로젝트 자료 임베딩 요청
        4. `Agent → Embedding Model` 프로젝트 자료 임베딩 요청 및 반환
        5. `Agent → Vector DB` 임베딩된 자료 저장
        6. `Web Server → RDB` 프로젝트 정보 저장
    2. 프로젝트 수정
        1. `Admin → Web UI` 프로젝트에 대한 수정 버튼 클릭
        2. `Web UI → Web Server → Agent` 프로젝트 정보 요청
        3. `Agent → Vector DB` 임베딩 자료 요청 및 반환(프로젝트 참여 인원 정보 등)
        4. `Agent → Embedding Model` 역임베딩 요청 및 반환 (Vector DB에서 가져온 정보)
        5. `Agent → RDB` 프로젝트 정보 요청 
        6. `RDB → (Agent → Web Server) → Web UI` 프로젝트 정보 반환
        7. `Web UI → Admin` 프로젝트 정보 출력
        8. `Admin → Web UI` 프로젝트 수정 클릭
        9. `Web UI → Web Server` 프로젝트 수정 요청
        10. `Agent → Embedding Model` 프로젝트 자료 임베딩 요청
        11. `Embedding Model → Agent` 임베딩 자료 반환
        12. `Agent → Vector DB` 임베딩된 자료 저장
        13. `Web Server → RDB` 프로젝트 정보 저장
    3. 초기 이슈 생성 요청
        1. `Admin → Web UI` 이슈 자동 생성 클릭
        2. `Web UI → Web Server → Agent` 이슈 자동 생성 요청
        3. `Agent → Vector DB` 설계 자료 검색 및 반환
        4. `Agent → Gemini` 이슈 생성 요청
        5. `Gemini → (Agent → Web Server) → Web UI` 생성된 이슈 리스트 반환
        6. `Web UI → Admin` 생성된 이슈 리스트 출력
        7. a ~ g 반복
        8. `Admin → Web UI` 전체 이슈 확정
        9. `Web UI → Web Server → Agent` 이슈 담당자 배정 요청
        10. `Agent → Gemini` 이슈 담당자 배정 요청
        11. `Gemini → (Agent → Web Server) → Web UI` 이슈 담당자 배정 반환
        12. `Web UI → Admin` 이슈 담당자 배정 출력
        13. `Admin → Web UI` 이슈 담당자 수정
        14. `Admin → Web UI` 전체 이슈 생성 클릭
        15. `Web UI → Web Server` 이슈 생성 요청
        16. `Web Server → Github` 이슈 생성 요청
    4. 이슈 추가
        1. `Admin → Web UI` 이슈 내용 입력
        2. `Admin → Web UI` AI 배정 요청 (Assignee, Sprint, 등등)
        3. `Web UI → Web Server → Agent` AI 배정 요청
        4. `Agent → Gemini` AI 배정 요청 및 반환
        5. `Agent → Web Server → Web UI` AI 배정 결과 반환
        6. `Web UI → Admin` 배정 결과 출력
        7. b~f 반복
        8. `Admin → Web UI` 이슈 추가 클릭
        9. `Web UI → Web Server → Github` 이슈 추가 요청
    5. 이슈 수정
        1. `Admin → Web UI` 이슈 선택
        2. `Web UI → Web Server` 이슈 정보 요청
        3. `Web Server → Web UI` 세부 이슈 정보 반환
        4. `Web UI → Admin` 이슈 정보 반환
        5. `Admin → Web UI` 이슈 내용 수정
        6. `Admin → Web UI` 이슈 수정 클릭
        7. `Web UI → Web Server → Github` 이슈 수정 요청
    6. 이슈 삭제
        1. `Admin → Web UI` 이슈 선택
        2. `Web UI → Web Server` 이슈 정보 요청
        3. `Web Server → Web UI` 세부 이슈 정보 반환
        4. `Web UI → Admin` 이슈 정보 반환
        5. `Admin → Web UI` 이슈 삭제 클릭
        6. `Web UI → Web Server → Github` 이슈 삭제 요청
    7. 변경 요청서 확인
        1. `Admin → Web UI` 변경 요청서 확인 클릭
        2. `Web UI → Web Server` 일정 변경 요청서 목록 조회
        3. `Web Server → RDB` 일정 변경 요청서 목록 조회 및 반환
        4. `Web Server → Web UI` 일정 변경 요청서 목록 반환
        5. `Web UI → Admin` 변경 요청서 목록 출력
        6. `Admin → Web UI` 변경 요청서 선택
        7. `Web UI → Web Server → Agent` 일정 변경 요청서 피드백 요청
        8. `Agent → Vector DB` 팀원 역량 정보 요청 및 반환
        9. `Agent → RDB` 프로젝트 정보 요청 및 반환
        10. `Agent → Github` 이슈 정보 요청 및 반환
        11. `Agent → Gemini` 일정 변경 요청서 피드백 요청 및 반환
        12. `Agent → Web Server → Web UI` 일정 변경 요청서 피드백 반환
        13. `Web UI → Admin` 일정 변경 요청서 피드백 출력
        14. `Admin → Web UI` 일정 변경 승인 클릭
            1. `Web UI → Web Server` 일정 변경 승인 요청
            2. `Web Server → RDB` 일정 변경 요청서 삭제
            3. `Web Server → Github` 이슈 수정 요청
            4. `Web Server → Bot Server` User 변경 승인 알림 요청
            5. `Bot Server → Bot UI` 일정 변경 요청 승인 알림 전달
            6. `Bot UI → User` 일정 변경 요청 승인 알림 출력
        15. `Admin → Web UI` 일정 변경 반려 클릭
            1. `Web UI → Web Server` 일정 변경 반려 요청
            2. `Web Server → RDB` 일정 변경 요청서 삭제
            3. `Web Server → Bot Server` User 변경 반려 알림 요청
            4. `Bot Server → Bot UI` 일정 변경 요청 반려 알림 전달
            5. `Bot UI → User` 일정 변경 요청 반려 알림 출력
- User
    1. 배정된 업무 알림
        1. `Bot UI → User` Sprint 내 할당 업무 알림
            - 이번 sprint에 배정된 sprint 정보, 이슈 번호, 이슈 타이틀, 이슈 요약, 이슈 링크 정보를 봇을 이용해 전송
    2. 마감기한 초과 예상 알림
        1. `Bot UI → User` 마감기한 초과 예상 이슈 알림
            - LLM이 사용자의 역량 정보와 할당된 이슈의 기간 정보를 파악하여 해당 sprint 기간 내에 다 끝내지 못할 것 같은 이슈에 대한 경고 알림
    3. 일정 변경 요청
        1. `User → Bot UI` 일정 변경 요청
            - 변경할 이슈의 일정, 변경 사유 작성
"""

issue_template = PromptTemplate(
    input_variables=["issue_name"],
    template=(
        """
        {
            "type": "Enter the development roles (e.g., Backend, Frontend, AI, etc.).",
            "name": "issue_name",
            "description": "Please propose a new feature, UI improvement, or documentation enhancement.",
            "title": "[Feature]: ",
            "labels": ["✨ Feature"],
            "body": [
                {
                    "id": "description",
                    "attributes": {
                        "label": "Feature Description",
                        "description": "Please describe the feature in detail. What problem does it solve, and how can it contribute to the project?",
                        "placeholder": "Please clearly describe the feature.",
                        "value": "- Core keyword\\n- Description 1\\n- Description 2\\n- Description 3"
                    }
                },
                {
                    "id": "todos",
                    "attributes": {
                        "label": "Implementation Steps (TODO)",
                        "description": "Please outline the steps required to implement this feature.",
                        "value": "- [ ] TODO 1\\n- [ ] TODO 2\\n- [ ] TODO 3"
                    }
                },
                {
                    "id": "wish-assignee-info",
                    "attributes": {
                        "label": "Desired Assignee Information",
                        "description": "Please describe the criteria for a suitable assignee for this issue.",
                        "placeholder": "Please fill out the following items.",
                        "value": "- Troubleshooting Score: \\n- Project Contribution Score: \\n"
                    }
                }
            ]
        }
        """
    )
)

feature_example = (
    "Web UI: Implement Login Button\n",
    "Web Server: Implement Login Request Endpoint\n",
    "Vector DB: Store User Information\n",
    "Embedding Model: Embed User Information\n",
    "Gemini: Generate Issue Template\n"
)

decomposition_prompt_template = PromptTemplate(
    input_variables=["documents"],
    template=(
        "You are an expert project manager AI. Given the development project document below, "
        "decompose the project into actionable steps.\n\n"
        "Documents:\n{documents}\n\n"
        "Steps:"
    )
)

rag_prompt_template = PromptTemplate(
    input_variables=["original_prompt", "context"],
    template=(
        "Answer the question based on the context below.\n\n"
        "Context: {context}\n\n"
        "Question: {original_prompt}\n\n"
        "Answer:"
    )
)