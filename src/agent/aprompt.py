from langchain.prompts import PromptTemplate

# -------------------------------------------------------------------------------
# Prompts for feedback generation
# -------------------------------------------------------------------------------

feedback_template = PromptTemplate(
    input_variables=["project_info", "reason", "issue", "stats", "output_example"],
    template=(
        "project_info: {project_info}\n"
        "reason for rescheduling: {reason}\n"
        "issue: {issue}\n"
        "stats: {stats}\n\n"
        "Due to the reason for modification, either the assignee or the due date of the issue needs to be updated.\n"
        "Based on the issue content and team member skill profiles, please suggest the following two options:\n"
        "	1.	Propose a new assignee who is suitable for handling this issue.\n"
        "	2.	Instead of changing the assignee, propose a new due date that aligns with the team’s defined sprint interval.\n" \
        "Refer to sprint unit from project_info, and suggest a new sprint number.\n"
        "Please provide a detailed explanation for each suggestion in output format not outside of belowing format, including the reasons for the proposed changes.\n"
        "Output must be in the following format:\n"
        "{output_example}\n"
        "You must not include your analysis beside the output.\n"
    )
)

feedback_output_example = (
    """
        {
            "issue_id": "ISSUE-123",
            "modification_reason": "The original assignee is overloaded during this sprint.",
            "suggestions": {
                "new_assignee": {
                "name": "Alice Kim",
                "reason": "Alice has prior experience with similar issues and has available capacity this sprint."
                },
                "new_sprint": {
                "sprint": 4,
                "reason": "Extending the deadline by one sprint cycle (2 weeks) to accommodate current workload."
                }
            }
        }
    """
)

# -------------------------------------------------------------------------------
# Prompts for Developer Assignment
# -------------------------------------------------------------------------------

recommend_assignee_template = PromptTemplate(
    input_variables=["project_id", "issues"],
    template=(
        "Project Id: {project_id}\n"
        "What you have to do is recommend assignees for the issues.\n"
        "You must recommend assignees for each issue in the project.\n"
        "This is order to recommend assignees that you must follow:\n"
        "0. Get project information from the project ID.\n"
        "1. Get user stats from database.\n"
        "2. Recommend assignees for each issue based on the user stats and issues.\n"
        "3. Format of each issue must match with assign_input_template and assign_output_example\n"
        "4. Each values of the template for each issue must be written in Korean.\n"
        "5. Your output must be contains only the issues in a list of json.\n"
    )
)

assign_issue_template = PromptTemplate(
    input_variables=["input_file", "output_example"],
    template=(
        "**Input Description**\n"
        "'input file' : {input_file}"
        "The input file includes the following fields:\n"
        "- **Project Name**: Overall title of the project\n"
        "- **Development Overview**: A short description of the system’s purpose and features\n"
        "- **Planned Issues**: A list of structured GitHub-style issues, each containing:\n"
            "- type, title, labels, description\n"
            "- TODOs\n"
            "- additional context\n"
            "- desired developer requirements (scores, field, etc.)\n"
        "- **Developers**: A list of developers with the following information:\n"
            "- Name\n"
            "- Field (Frontend / Backend / AI)\n"
            "- Experience Level (e.g., Junior / Intermediate / Senior)\n"
            "- Troubleshooting Score (0–100)\n"
            "- Project Contribution Score (0–100)\n"
            "- Implemented Features (list of experience)\n"

        "**Assignment Criteria**\n"
        "Assign developers based on the following principles:\n"
        "1. **Skill Match**: The developer’s field and implemented features should align with the issue’s required stack or type.\n"  
        "2. **Relevant Experience**: Prior work or commits that show experience with similar features or systems.\n"  
        "3. **Troubleshooting Score**: Higher scores indicate stronger problem-solving skills.\n"  
        "4. **Project Contribution Score**: Reflects reliability and initiative.\n"  
        "5. **Timeliness Potential**: Prefer developers likely to deliver on time for high-priority or high-difficulty issues.\n"
        "6. **Team Dynamics**: Consider team members' workload and collaboration potential.\n\n"

        "**Real-World Constraints and Exceptions**\n"
        "- If **no developer exactly meets** all score thresholds for an issue, assign the **most suitable developer(s)** who come **closest** to the requirements, and explain why they were chosen anyway.\n"
        "- If the issue appears **complex or multi-step**, consider assigning **more than one developer**, especially if their expertise complements each other.\n\n"

        "**Task**\n"
        "For each issue in the input file, assign the most appropriate 1–2 developers from the provided developer list.\n"  
        "Provide a clear, detailed justification for each assigned developer based on the criteria above.\n"  
        "Include explanations if a developer doesn’t fully meet a score requirement but is still assigned.\n"  
        "Try to minimize overloading any single developer with too many tasks, unless necessary.\n\n"
        
        "Do not include your analysis or reasoning in the output.\n"
        "Write issue title, name of assigned developers, and their description in the output.\n"
        "names of assigned developers should be ones of the developers in the user stats.\n"
        "You must assign at least one developer to each issue.\n"
        "Output must include three fields: issue, assignee, and description.\n"
        "Output must be in following format:\n"
        "**Output Format**\n"
        "{output_example}"
    )
)

assign_input_template = PromptTemplate(
    input_variables=["project_name", "project_overview", "issues", "stats"],
    template=(
        "project_name: {project_name}\n"
        "project_overview: {project_overview}\n"
        "issues: {issues}\n"
        "stats: {stats}\n\n"
    )
)

assign_output_example = (
    """
        [
            {
                "issue": "Issue title",
                "assignee": "Assigned Developer Names will be here",
                "description": [
                    "Developer1: Backend, experience with API development and session management. Troubleshooting: 85, Contribution: 90. Assigned due to strong alignment with backend stack and history of relevant features.",
                    "Developer2: Frontend, worked on dashboard UI and error handling. Troubleshooting: 78, Contribution: 75. Assigned to support interface integration and ensure reliability."
                ]
            },
        ]
    """
)

# -------------------------------------------------------------------------------
# Prompts for Competency Assessment
# -------------------------------------------------------------------------------

assess_stat_template = PromptTemplate(
    input_variables=["user_id"],
    template=(
        "User ID: {user_id}\n"
        "What you have to do is assess the competency of a user based on their GitHub activity.\n"
        "You must analyze the user's GitHub activity and generate a JSON file with the following fields:\n"
        "This is the order to do your task:\n"
        "0. Get selected repositories of the user from database.\n"
        "1. Get GitHub activation data of the user from selected repositories.\n"
        "2. Assess the user's competency based on the GitHub activation data.\n"
        "   - If github activation data is empty, you can give 0 point.\n"
        "3. Store the assessment result in a JSON file with the following fields:\n"
        "4. Result must include the following fields:\n"
        "- **Name**: User's name\n"
        "- **Field**: User's field (Backend, Frontend, AI, etc.)\n"
        "- **Experience**: User's experience level (Junior, Middle, Senior, etc.)\n"
        "- **Evaluation Scores**: A dictionary containing the following fields:\n"
            "- **Project Contribution Scoring**: A dictionary containing the score and justification for project contribution.\n"
            "- **Troubleshooting Scoring Criteria**: A dictionary containing the score and justification for troubleshooting.\n"
        "- **Implemented Features**: A list of features that the user has implemented based on their GitHub activity.\n"
        "5. The output must be a valid JSON file and do not include your additional analysis.\n"

    )
)

define_stat_prompt = PromptTemplate(
    input_variables=["user_name", "criteria_table", "github_activation_data" , "info_file", "output_example"],
    template=(
        "You are an expert software engineering analyst. Your task is to analyze commit and pull request data, score contributions based on predefined criteria, and augment a JSON file with the results.\n"
        "**Input Files:**\n"
            "1.  **Criteria Table:** {criteria_table} (This  contains the troubleshooting and project contribution scoring rubric, as previously provided.  Assume it's readily available to you with that filename.)\n"
            "2.  **Commit and Pull Request Data:** {github_activation_data} (This file contains the commit history and pull request contents for one or more repositories. The format is unstructured text but should be understandable for analysis.)\n"
            "3.  **Info File:** {info_file} (This file is a JSON template where you will add the analysis results.  Initially, it may be empty or contain placeholder fields.)\n\n"
            "In Info File, write user name as {user_name}, field, and experience level.\n"
            "The field can be Backend, Frontend, AI, etc.\n"
            "The experience level can be Junior, Middle, Senior, etc.\n\n"
        "**Task:**\n"
            "1.  **Analyze Commit and Pull Request Data:**  Thoroughly examine the contents of `github_data.json`. Identify key activities, contributions, and issues addressed in the commits and pull requests.  Focus on the type of work done (feature implementation, bug fixes, documentation, etc.) and the level of contribution (major, minor, etc.).\n"
            "2.  **Score Contributions:** Using the `scoring_criteria.json` file as a guide, assign scores for both 'Troubleshooting' and 'Project Contribution' based on your analysis of the `github_data.json` file.  Justify each score briefly (1-2 sentences) based on specific examples found in the commit/PR data.\n"
            "3.  **Extract Implemented Features:** Based on the commit messages and pull request descriptions in `github_data.json`, identify a list of commonly recognized features that have been implemented. Examples of features are: 'User Authentication', 'Log Management', 'Static Page Rendering', 'API Endpoint Creation', etc. Aim for a comprehensive but concise list.\n"
            "4.  **Update Info File:** Modify the contents of `Info File` to include the following:\n\n"

        "*   Add a section called `evaluation_scores` with the 'Troubleshooting' and 'Project Contribution' scores, including your justification for each score.\n"
        "*   Add a section called `implemented_features` containing a list of the features identified.\n"
        "**Output:**"
        "Provide the complete, updated contents of `Info File` as your response. The JSON must be valid. The structure should include the original content of `Info File` (if any), plus the new `evaluation_scores` and `implemented_features` sections.  The keys should be in snake_case.\n\n"
        "**Example Output:**\n"
        "{output_example}\n\n"
    ),
)

score_table = (
    """
            project_contribution:
        - score: 90-100
            description: "Contributed significantly to core feature planning and implementation, adoption of key technologies, team leadership, and thorough reviews and documentation."
        - score: 70-89
            description: "Played a major role in implementing key features, performance improvements, test coverage enhancements, and actively participated in code reviews."
        - score: 50-69
            description: "Contributed to feature implementation, bug fixes, and team communication."
        - score: 30-49
            description: "Developed partial features, committed sporadically, and participated minimally in reviews."
        - score: 0-29
            description: "Had very few commits or contributions."

        troubleshooting:
        - score: 90-100
            description: "Demonstrated rapid root cause analysis and resolution in complex failure scenarios, eliminated underlying issues, and provided detailed RCA documentation."
        - score: 70-89
            description: "Possessed significant experience in resolving major issues, identifying causes, and implementing temporary or permanent fixes."
        - score: 50-69
            description: "Capable of addressing common bugs and errors, analyzing logs, and determining root causes."
        - score: 30-49
            description: "Able to solve simple issues but requires assistance for complex situations."
        - score: 0-29
            description: "Lacks troubleshooting experience or has very few contributions."
    """

)

info_file = (
    """
        {
            "Name": ,
            "Field": ,
            "Experience": ,
        }
    """
)

define_stat_output_example = (
    """
        {
            "Name": "송재훈",
            "Field": "Backend",
            "Experience": "Junior",
            "evaluation_scores": {
                "project_contribution_scoring": {
                    "score": "75",
                    "justification": "Played a major role in implementing key features (e.g., authentication, data handling across multiple projects like GDG, happyaginginc, profitnote) and actively participated in project setup and maintenance (e.g., templates, dependencies)."
                },
                "troubleshooting_scoring_criteria": {
                    "score": "80",
                    "justification": "Possessed significant experience resolving diverse issues (UI, logic, data, config) across multiple projects, as shown by numerous 'fix' and 'hotfix' commits addressing problems like validation, CORS, state management, and API errors."
                }
            },
            "implemented_features": [
                "User Authentication (Social Login, JWT, Session Management)",
                "API Development (CRUD, RESTful)",
                "Database Interaction / Management (SQL, ORM-like patterns, DDL/DML)",
                "UI Development & Component Design (Web, Mobile)",
                "State Management (Frontend - Recoil, Provider)",
                "Asynchronous Programming / API Integration",
                "Error Handling & Input Validation",
                "Configuration & Build Management (Dependencies, Deployment, CORS)",
                "Mobile Application Development (Flutter, React Native suspected)",
                "Web Application Development (React suspected, SPA)",
                "Version Control Best Practices (Conventional Commits, PR Templates, Issue Linking)",
                "Basic System Programming Concepts (C - File I/O, Error Handling)"
            ]
        }
    """
)

# -------------------------------------------------------------------------------
# Prompts for Issue Generation
# -------------------------------------------------------------------------------

generate_issue_template = PromptTemplate(
    input_variables=["project_id", "feature_example"],
    template=(
        "Project Id: {project_id}\n"
        "What you have to do is generate a list of issues for the project.\n"
        "You must generate the issues in order of development sequence.\n"
        "You must generate the issues in a way that they can be completed within one sprint.\n"
        "This is order to generate issues that you must follow:\n"
        "0. Get project information from the project ID.\n"
        "1. Get and Analyze documents of the project.\n"
        "2. Define 2 features(tasks) as a list needed to complete the project without any descriiptions like this example {feature_example}.\n"
        "3. Generate a issue for each task.\n"
        "4. Format of each issue must match with issue_template (get issue_template) and fill values of the template\n"
        "5. Each values of the template for each issue must be written in Korean.\n"
        "6. Your output must be contains only the issues in a list of json.\n"
    )
)

make_issue_template = PromptTemplate(
    input_variables=["project_info", "documents", "issue_template", "features"],
    template=(
        "Analyze the planning/design documents.\n"
        "Write the implementation steps for each feature.\n"
        "Write any additional information and reference materials required to implement each feature.\n"
        "Write the criteria for the personnel required for each feature in terms of scores, based on the score table.\n"
        "Write sprint number for each feature considering the project schedule and dependency of each feature.\n"
        "Sprint unit(days) is defined in the project information.\n"
        "If sprint unit is 7, it means 7 days.\n"
        "If sprint unit is 14, it means 14 days.\n" 
        "If sprint of issue is 1, it means the issue should be completed in the first sprint.\n"
        "If sprint of issue is 2, it means the issue should be completed in the second sprint.\n"
        "Each task should be written according to the issue template.(Must include contents of type, name, description, title, labels, body)\n"
        "All contents in the issue template should be written in Korean.\n"
        "Name(right of ':'), description on the top in the issue template should be written in Korean.\n"
        
        "Make only one issue per each issue name.\n"
        "The output should be a list of complete tasks in json.\n\n"

        "Project information: {project_info}\n\n"
        "Planning/Design Documents: {documents}\n\n"
        "Issue template with Example Value: {issue_template}\n\n"
        "Issue names: {features}"
    )
)

issue_template = PromptTemplate(
    input_variables=["issue_name"],
    template=(
        """
        {
            "type": "Enter the development roles (Backend, Frontend, AI).",
            "name": "issue_name",
            "description": "Please propose a new feature, UI improvement, or documentation enhancement.",
            "title": "[Feature]: ",
            "labels": ["✨ Feature"],
            "sprint": "refer to sprint unit in project information",
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
    "[Feat]: Implement Login Button\n",
    "[Feat]: Implement Login Request Endpoint\n",
    "[Feat]: Store User Information\n",
    "[Feat]: Embed User Information\n",
    "[Feat]: Generate Issue Template\n",
    "[Refactor]: Refactor User Information Storage\n",
    "[Refactor]: Refactor User Information Embedding\n",
    "[Test]: Test Login Button\n",
    "[Test]: Test Login Request Endpoint\n",
)

made_issue_example = (
    """
        [
            {
                "type": "✨ Feature",
                "name": "AI 에이전트 구현",
                "description": "AI Agent가 설계 내용 및 개발 진행 상황을 바탕으로 필요한 이슈들을 제안하고, LLM 생성된 레포지토리 정보와 기획 및 설계 내용, 개발 진행 상황 등을 에게 전달하여 이슈를 제안합니다. 제안된 이슈는 일관된 템플릿으로 작성되며 사용자의 동의를 얻어 생성합니다. 스프린트 단위로 이슈를 지속적으로 제안하며, AI Agent는 전체 프로젝트 로드맵을 인지하고 있으며 사용자의 선택에 따라 현재 스프린트에 대한 이슈만을 보여주거나 전체 이슈를 확인할 수 있도록 합니다.",
                "title": "[Feature]: AI 에이전트 구현",
                "labels": [
                    "✨ Feature"
                ],
                "sprint": 1,
                "priority": "M",
                "body": [
                    {
                        "id": "description",
                        "attributes": {
                            "label": "기능 설명",
                            "description": "기능을 자세히 설명해주세요. 어떤 문제를 해결하고 프로젝트에 어떻게 기여할 수 있나요?",
                            "placeholder": "기능을 명확하게 설명해주세요.",
                            "value": "- 핵심 키워드: AI 에이전트, 이슈 제안, LLM\n- 설명 1: AI 에이전트가 프로젝트 정보를 기반으로 이슈를 제안합니다.\n- 설명 2: 제안된 이슈는 템플릿에 따라 작성됩니다.\n- 설명 3: 사용자는 제안된 이슈를 확인하고 생성 여부를 결정할 수 있습니다."
                        }
                    },
                    {
                        "id": "todos",
                        "attributes": {
                            "label": "구현 단계 (TODO)",
                            "description": "이 기능을 구현하는 데 필요한 단계를 간략하게 설명해주세요.",
                            "value": "- [ ] TODO 1: LLM 연동 및 API 연동\n- [ ] TODO 2: 이슈 템플릿 정의 및 적용\n- [ ] TODO 3: 사용자 인터페이스 개발 (이슈 제안 확인 및 생성)\n- [ ] TODO 4: 스프린트 단위 이슈 제안 기능 구현\n- [ ] TODO 5: 전체 로드맵 인지 및 이슈 필터링 기능 구현"
                        }
                    },
                    {
                        "id": "wish-assignee-info",
                        "attributes": {
                            "label": "희망 담당자 정보",
                            "description": "이 이슈에 적합한 담당자의 기준을 설명해주세요.",
                            "placeholder": "다음 항목을 작성해주세요.",
                            "value": "- 문제 해결 능력 점수: 80점 이상\n- 프로젝트 기여도 점수: 70점 이상\n- LLM 이해도: 80점 이상\n- API 연동 경험: 필수"
                        }
                    }
                ]
            },
            {
                "type": "✨ Feature",
                "name": "실시간 프로젝트 모니터링 대시보드 구현",
                "description": "이슈들을 추적하고 반복적으로 알림을 제공하며, 각 팀원마다 완료한 이슈 개수, 예정된 이슈 개수, 현재 무엇을 하고 있는지 보여줍니다. 프로젝트 전체 진행률 및 프로젝트 활성화 정도를 제공합니다.",
                "title": "[Feature]: 실시간 프로젝트 모니터링 대시보드 구현",
                "labels": [
                    "✨ Feature"
                ],
                "sprint": 2,
                "priority": "M",
                "body": [
                    {
                        "id": "description",
                        "attributes": {
                            "label": "기능 설명",
                            "description": "기능을 자세히 설명해주세요. 어떤 문제를 해결하고 프로젝트에 어떻게 기여할 수 있나요?",
                            "placeholder": "기능을 명확하게 설명해주세요.",
                            "value": "- 핵심 키워드: 대시보드, 실시간 모니터링, 프로젝트 진행률\n- 설명 1: 프로젝트 진행 상황을 실시간으로 모니터링할 수 있는 대시보드를 제공합니다.\n- 설명 2: 팀원별 이슈 진행 상황을 시각적으로 보여줍니다.\n- 설명 3: 프로젝트 전체 진행률 및 활성화 정도를 제공합니다."
                        }
                    },
                    {
                        "id": "todos",
                        "attributes": {
                            "label": "구현 단계 (TODO)",
                            "description": "이 기능을 구현하는 데 필요한 단계를 간략하게 설명해주세요.",
                            "value": "- [ ] TODO 1: 데이터 수집 및 API 연동 (이슈, 팀원 정보 등)\n- [ ] TODO 2: 대시보드 UI 디자인 및 개발\n- [ ] TODO 3: 실시간 데이터 업데이트 기능 구현\n- [ ] TODO 4: 팀원별 이슈 진행 상황 시각화\n- [ ] TODO 5: 프로젝트 진행률 및 활성화 정도 계산 및 표시"
                        }
                    },
                    {
                        "id": "wish-assignee-info",
                        "attributes": {
                            "label": "희망 담당자 정보",
                            "description": "이 이슈에 적합한 담당자의 기준을 설명해주세요.",
                            "placeholder": "다음 항목을 작성해주세요.",
                            "value": "- UI/UX 디자인 점수: 85점 이상\n- 프론트엔드 개발 능력 점수: 90점 이상\n- 데이터 시각화 능력: 80점 이상\n- API 연동 경험: 필수"
                        }
                    }
                ]
            }
        ]
    """
)