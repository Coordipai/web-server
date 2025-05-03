from langchain.prompts import PromptTemplate


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