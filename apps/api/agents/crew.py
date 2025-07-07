from crewai import Crew, Process
from .strategy_agent import get_strategy_agent, get_strategy_task

def get_crew(prompt: str):
    agent = get_strategy_agent()
    task = get_strategy_task(prompt)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        process=Process.sequential
    )
    return crew
