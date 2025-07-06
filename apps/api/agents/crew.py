from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from typing import Dict, Any, List
from core.settings import settings
from core.llm import generate_content

class VertexCrew:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-70b-8192"
        )

    def create_strategy_agent(self) -> Agent:
        """Create a DevRel strategy agent"""
        return Agent(
            role="DevRel Strategy Expert",
            goal="Develop comprehensive DevRel strategies that drive developer engagement and community growth",
            backstory="""You are an experienced DevRel strategist with deep knowledge of developer communities,
            technical content creation, and community building. You understand the developer mindset and can
            create strategies that resonate with technical audiences.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_content_agent(self) -> Agent:
        """Create a DevRel content agent"""
        return Agent(
            role="DevRel Content Creator",
            goal="Create engaging technical content that educates and inspires developers",
            backstory="""You are a skilled technical content creator who specializes in making complex topics
            accessible to developers. You excel at creating blog posts, tutorials, documentation, and social
            media content that developers love to read and share.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_community_agent(self) -> Agent:
        """Create a DevRel community agent"""
        return Agent(
            role="DevRel Community Manager",
            goal="Build and nurture developer communities through engagement and events",
            backstory="""You are an expert community manager who understands how to build and grow developer
            communities. You know how to create engaging events, foster meaningful discussions, and build
            relationships with developers and technical influencers.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_analytics_agent(self) -> Agent:
        """Create a DevRel analytics agent"""
        return Agent(
            role="DevRel Analytics Expert",
            goal="Measure and optimize DevRel performance through data-driven insights",
            backstory="""You are a data-driven DevRel analyst who understands how to measure the success of
            developer relations efforts. You can identify key metrics, create dashboards, and provide insights
            that help optimize DevRel strategies.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def create_strategy_task(self, prompt: str) -> Task:
        """Create a strategy development task"""
        return Task(
            description=f"""
            Analyze the following DevRel request and create a comprehensive strategy:

            Request: {prompt}

            Your strategy should include:
            1. Strategic overview and objectives
            2. Target audience analysis
            3. Key messaging and positioning
            4. Content and engagement tactics
            5. Success metrics and KPIs
            6. Implementation timeline
            7. Resource requirements

            Provide a detailed, actionable strategy that can be executed by a DevRel team.
            """,
            agent=self.create_strategy_agent()
        )

    def create_content_task(self, strategy_context: str) -> Task:
        """Create a content creation task"""
        return Task(
            description=f"""
            Based on the following DevRel strategy, create comprehensive content plans:

            Strategy Context: {strategy_context}

            Create content plans for:
            1. Blog post outlines and topics
            2. Social media content calendar
            3. Newsletter content ideas
            4. Video and webinar scripts
            5. Documentation improvements
            6. Technical tutorial series

            Focus on content that educates, engages, and inspires the developer community.
            """,
            agent=self.create_content_agent()
        )

    def create_community_task(self, content_context: str) -> Task:
        """Create a community building task"""
        return Task(
            description=f"""
            Based on the content strategy, develop community engagement plans:

            Content Context: {content_context}

            Develop plans for:
            1. Community engagement tactics
            2. Event ideas and formats
            3. Partnership opportunities
            4. Community building activities
            5. Feedback collection methods
            6. Influencer outreach strategies

            Focus on building authentic relationships with developers and creating value for the community.
            """,
            agent=self.create_community_agent()
        )

    def create_analytics_task(self, community_context: str) -> Task:
        """Create an analytics and measurement task"""
        return Task(
            description=f"""
            Based on the community strategy, create measurement and analytics plans:

            Community Context: {community_context}

            Develop measurement plans for:
            1. Key performance indicators (KPIs)
            2. Data collection strategies
            3. Reporting dashboards
            4. Success benchmarks
            5. Optimization recommendations
            6. ROI measurement methods

            Focus on actionable metrics that demonstrate DevRel value and guide optimization.
            """,
            agent=self.create_analytics_agent()
        )

    async def run_devrel_workflow(self, prompt: str) -> Dict[str, Any]:
        """Run the complete DevRel workflow"""
        try:
            # Create agents
            strategy_agent = self.create_strategy_agent()
            content_agent = self.create_content_agent()
            community_agent = self.create_community_agent()
            analytics_agent = self.create_analytics_agent()

            # Create tasks
            strategy_task = self.create_strategy_task(prompt)
            content_task = self.create_content_task("")  # Will be updated with strategy result
            community_task = self.create_community_task("")  # Will be updated with content result
            analytics_task = self.create_analytics_task("")  # Will be updated with community result

            # Create crew
            crew = Crew(
                agents=[strategy_agent, content_agent, community_agent, analytics_agent],
                tasks=[strategy_task, content_task, community_task, analytics_task],
                process=Process.sequential,
                verbose=True
            )

            # Run the crew
            result = crew.kickoff()

            return {
                "status": "completed",
                "result": result,
                "workflow": "devrel_strategy"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "workflow": "devrel_strategy"
            }

# Global instance
vertex_crew = VertexCrew()
