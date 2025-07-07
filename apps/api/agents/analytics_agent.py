from crewai import Agent, LLM

llm = LLM(model="groq/llama-3.1-8b")

def get_analytics_agent():
    return Agent(
        role="Analytics Agent",
        goal="Analyze campaign metrics and suggest optimizations",
        backstory="Data-driven analyst for DevRel campaigns.",
        tools=[],
        memory=True,
        llm=llm,
        verbose=True
    )
