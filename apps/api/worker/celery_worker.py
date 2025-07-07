from celery import Celery, chain
from typing import Dict, Any, Optional
from core.settings import settings
from core.llm import generate_content, analyze_text
from core.embeddings import embed_single
from core.moz import get_domain_overview, get_keyword_difficulty
import json

celery_app = Celery(
    "vertex_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def run_strategy_task(flow_id: str, project_id: str, prompt: str) -> Dict[str, Any]:
    """Run strategy agent task"""
    try:
        # Generate strategy content
        strategy_prompt = f"""
        As a DevRel strategy expert, analyze the following request and provide a comprehensive strategy:

        Request: {prompt}

        Please provide:
        1. Strategic overview
        2. Key objectives
        3. Target audience analysis
        4. Success metrics
        5. Implementation timeline
        """

        strategy_content = generate_content(strategy_prompt)

        return {
            "task_id": "strategy",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "completed",
            "result": {
                "content": strategy_content,
                "type": "strategy"
            }
        }
    except Exception as e:
        return {
            "task_id": "strategy",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }

@celery_app.task
def run_content_task(flow_id: str, project_id: str, strategy_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run content agent task"""
    try:
        # Use strategy result if available
        context = ""
        if strategy_result and strategy_result.get("result"):
            context = strategy_result["result"]["content"]

        content_prompt = f"""
        As a DevRel content creator, create engaging content based on the following context:

        Context: {context}

        Please create:
        1. Blog post outline
        2. Social media content ideas
        3. Newsletter content
        4. Video script outline
        5. Content calendar suggestions
        """

        content_result = generate_content(content_prompt)

        return {
            "task_id": "content",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "completed",
            "result": {
                "content": content_result,
                "type": "content"
            }
        }
    except Exception as e:
        return {
            "task_id": "content",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }

@celery_app.task
def run_community_task(flow_id: str, project_id: str, content_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run community agent task"""
    try:
        context = ""
        if content_result and content_result.get("result"):
            context = content_result["result"]["content"]

        community_prompt = f"""
        As a DevRel community manager, create community engagement strategies based on:

        Content Context: {context}

        Please provide:
        1. Community engagement tactics
        2. Event ideas
        3. Partnership opportunities
        4. Community building activities
        5. Feedback collection methods
        """

        community_result = generate_content(community_prompt)

        return {
            "task_id": "community",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "completed",
            "result": {
                "content": community_result,
                "type": "community"
            }
        }
    except Exception as e:
        return {
            "task_id": "community",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }

@celery_app.task
def run_analytics_task(flow_id: str, project_id: str, community_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run analytics agent task"""
    try:
        context = ""
        if community_result and community_result.get("result"):
            context = community_result["result"]["content"]

        analytics_prompt = f"""
        As a DevRel analytics expert, provide measurement strategies for:

        Community Context: {context}

        Please provide:
        1. Key performance indicators
        2. Measurement tools and methods
        3. Reporting templates
        4. Data collection strategies
        5. Success benchmarks
        """

        analytics_result = generate_content(analytics_prompt)

        return {
            "task_id": "analytics",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "completed",
            "result": {
                "content": analytics_result,
                "type": "analytics"
            }
        }
    except Exception as e:
        return {
            "task_id": "analytics",
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }

@celery_app.task
def run_flow_task(flow_id: str, project_id: str, prompt: str) -> Dict[str, Any]:
    """Run complete flow task"""
    try:
        # Run the chain of tasks
        workflow = chain(
            run_strategy_task.s(flow_id, project_id, prompt),
            run_content_task.s(flow_id, project_id),
            run_community_task.s(flow_id, project_id),
            run_analytics_task.s(flow_id, project_id)
        )

        result = workflow()

        return {
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "completed",
            "task_chain": result
        }
    except Exception as e:
        return {
            "flow_id": flow_id,
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }

@celery_app.task
def analyze_seo_task(domain: str, keywords: list) -> Dict[str, Any]:
    """Analyze SEO metrics for a domain and keywords"""
    try:
        results = {
            "domain_overview": {},
            "keyword_analysis": {},
            "recommendations": []
        }

        # Get domain overview
        if settings.MOZ_API_KEY:
            try:
                results["domain_overview"] = get_domain_overview(domain)
            except Exception as e:
                results["domain_overview"] = {"error": str(e)}

        # Analyze keywords
        for keyword in keywords:
            try:
                if settings.MOZ_API_KEY:
                    results["keyword_analysis"][keyword] = get_keyword_difficulty(keyword)
                else:
                    results["keyword_analysis"][keyword] = {"difficulty": "N/A", "volume": "N/A"}
            except Exception as e:
                results["keyword_analysis"][keyword] = {"error": str(e)}

        # Generate SEO recommendations
        seo_prompt = f"""
        Based on the following domain and keyword analysis, provide SEO recommendations:

        Domain: {domain}
        Keywords: {', '.join(keywords)}

        Please provide:
        1. Content optimization suggestions
        2. Technical SEO improvements
        3. Link building opportunities
        4. Keyword targeting strategy
        5. Performance optimization tips
        """

        results["recommendations"] = generate_content(seo_prompt)

        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
