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
        "- If the issue appears **complex or multi-step**, consider assigning **more than one developer**, especially if their expertise complements each other.\n"
        "- If absolutely no reasonable candidate exists, only then set the issue as `Unassigned` and provide an explanation.\n\n"

        "**Task**\n"
        "For each issue in the input file, assign the most appropriate 1–2 developers from the provided developer list.\n"  
        "Provide a clear, detailed justification for each assigned developer based on the criteria above.\n"  
        "Include explanations if a developer doesn’t fully meet a score requirement but is still assigned.\n"  
        "Try to minimize overloading any single developer with too many tasks, unless necessary.\n\n"
        
        "Do not include your analysis or reasoning in the output.\n"
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
                "assignee": "Developer1, Developer2",
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

# -------------------------------------------------------------------------------
# Prompts for RAG
# -------------------------------------------------------------------------------

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