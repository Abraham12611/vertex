from crewai import Agent, LLM
from .pgvector_search_tool import PgVectorSearchTool
from .strategy_memory_tool import StrategyMemoryTool

llm = LLM(model="groq/llama-3.1-8b")
memory_tool = PgVectorSearchTool(api_url="http://localhost:8000", project_id="...")
strategy_memory_tool = StrategyMemoryTool()

def get_content_agent():
    return Agent(
        role="Content Agent",
        goal="Generate technical content and code samples",
        backstory="Prolific technical writer and code generator.",
        tools=[memory_tool, strategy_memory_tool],
        memory=True,
        llm=llm,
        verbose=True
    )
