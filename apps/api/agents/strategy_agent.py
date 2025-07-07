from crewai import Agent, Task, LLM
from core.llm import chat_completion
from .moz_insights_tool import MozInsightsTool
from .pgvector_search_tool import PgVectorSearchTool

llm = LLM(model="groq/llama-3.1-70b-versatile")  # or your preferred Groq model
moz_tool = MozInsightsTool()
memory_tool = PgVectorSearchTool(api_url="http://localhost:8000", project_id="...")

def get_strategy_agent():
    return Agent(
        role="Strategy Agent",
        goal="DevRel strategy and competitor analysis",
        backstory="Expert in developer relations and technical marketing.",
        tools=[moz_tool, memory_tool],
        memory=True,
        llm=llm,
        verbose=True
    )

def get_strategy_task(prompt: str):
    return Task(
        description=prompt,
        expected_output="A strategic DevRel plan.",
        agent=get_strategy_agent()
    )
