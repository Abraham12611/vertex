from crewai_tools.base import BaseTool
from core.moz import get_domain_overview, get_keyword_difficulty

class MozInsightsTool(BaseTool):
    def run(self, query: str):
        # query can be a domain or keyword
        if "." in query:
            return get_domain_overview(query)
        else:
            return get_keyword_difficulty(query)
