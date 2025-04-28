from src.agent import tool

class CustomAgentExecutor:
    def __init__(self):
        pass

    async def run(self, prompt: str) -> dict:
        decomposed_steps = await tool.decompose_task_tool(prompt)
        retrieved_contexts = []
        for step in decomposed_steps:
            context = tool.search_data_tool(step)
            retrieved_contexts.append({
                "step": step,
                "context": context
            })
        combined_context_lines = [
            f"단계: {item['step']}\n컨텍스트: {item['context']}" 
            for item in retrieved_contexts
        ]
        combined_context = "\n\n".join(combined_context_lines)
        final_prompt = tool.create_rag_prompt_tool(prompt, combined_context)
        llm_response = await tool.communicate_with_llm_tool(final_prompt)
        return {
            "original_prompt": prompt,
            "decomposed_steps": decomposed_steps,
            "retrieved_contexts": retrieved_contexts,
            "final_prompt": final_prompt,
            "llm_response": llm_response
        }
