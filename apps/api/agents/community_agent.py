from crewai import Agent, LLM
from .content_memory_tool import ContentMemoryTool

llm = LLM(model="groq/mixtral-8x7b-32768")
content_memory_tool = ContentMemoryTool()

def get_community_agent():
    return Agent(
        role="Community Agent",
        goal="Engage with developer community and craft social posts",
        backstory="Community manager and social media expert.",
        tools=[content_memory_tool],
        memory=True,
        llm=llm,
        verbose=True
    )
