from crewai import Crew, Process, Task
from agents.strategy_agent import get_strategy_agent
from agents.content_agent import get_content_agent
from agents.community_agent import get_community_agent
from agents.analytics_agent import get_analytics_agent

def get_devrel_flow(prompt: str):
    strategy_agent = get_strategy_agent()
    content_agent = get_content_agent()
    community_agent = get_community_agent()
    analytics_agent = get_analytics_agent()

    strategy_task = Task(
        description=f"DevRel strategy for: {prompt}",
        expected_output="Strategy plan with competitor insights.",
        agent=strategy_agent
    )
    content_task = Task(
        description="Generate blog/tutorial drafts and code samples.",
        expected_output="Markdown content and code.",
        agent=content_agent,
        dependencies=[strategy_task]
    )
    community_task = Task(
        description="Craft social posts and Discord replies.",
        expected_output="Social post drafts.",
        agent=community_agent,
        dependencies=[content_task]
    )
    analytics_task = Task(
        description="Analyze campaign metrics and suggest optimizations.",
        expected_output="JSON recommendations.",
        agent=analytics_agent,
        dependencies=[community_task]
    )

    crew = Crew(
        agents=[strategy_agent, content_agent, community_agent, analytics_agent],
        tasks=[strategy_task, content_task, community_task, analytics_task],
        verbose=True,
        process=Process.sequential
    )
    return crew
