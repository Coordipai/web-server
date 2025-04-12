from langchain.prompts import PromptTemplate

decomposition_template = PromptTemplate(
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

define_feature_template = PromptTemplate(
    input_variables=["documents", "issue_template"],
    template=(
        "Analyze the planning/design documents.\n"
        "Break down and define the development tasks needed to complete the project.\n"
        "Divide the tasks such that each task can be completed within one hour.\n"
        "List the divided tasks in order of development sequence.\n"
        "Each task should be written according to the issue template.\n"
        "The output should be a list of tasks in json.\n\n"

        "Planning/Design Documents: {documents}\n\n"
        "Issue template with Example Value: {issue_template}\n\n"
    )
)

complete_feature_template = PromptTemplate(
    input_variables=["documents", "features","score_table", "issue_template"],
    template=(
        "Analyze the planning/design documents.\n"
        "Write the implementation steps for each feature.\n"
        "Write any additional information and reference materials required to implement each feature.\n"
        "Write the criteria for the personnel required for each feature in terms of scores, based on the score table.\n"
        "Each task should be written according to the issue template.\n"
        "All contents in the issue template should be written in Korean.\n"
        "Name, description on the top in the issue template should be written in Korean.\n"
        "List the divided tasks in order of development sequence.\n"
        "The output should be a list of tasks in json.\n\n"

        "Planning/Design Documents: {documents}\n\n"
        "Features: {features}\n\n"
        "Score Table: {score_table}\n\n"
        "Issue template with Example Value: {issue_template}\n\n"
    )
)
