import requests
from typing import Dict, Any, List, Optional
from core.settings import settings

class MozAPI:
    def __init__(self):
        self.api_key = settings.MOZ_API_KEY
        self.secret_key = settings.MOZ_SECRET_KEY
        self.api_url = "https://api.moz.com/jsonrpc"

    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Moz API"""
        if not self.api_key:
            raise Exception("Moz API key not configured")

        headers = {
            "x-moz-token": self.api_key,
            "Content-Type": "application/json"
        }

        body = {
            "jsonrpc": "2.0",
            "id": "vertex",
            "method": method,
            "params": {"data": params}
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=body)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise Exception(f"Moz API error: {result['error']}")

            return result.get("result", {})
        except requests.RequestException as e:
            raise Exception(f"Moz API request failed: {str(e)}")

    def get_domain_overview(self, domain: str) -> Dict[str, Any]:
        """Get domain overview metrics"""
        return self._make_request("DataSiteMetricsFetchMultipleAction", {"targets": [domain]})

    def get_keyword_difficulty(self, keyword: str) -> Dict[str, Any]:
        """Get keyword difficulty metrics"""
        return self._make_request("DataKeywordMetricsOpportunityFetchAction", {"keyword": keyword})

    def get_keyword_suggestions(self, keyword: str) -> Dict[str, Any]:
        """Get keyword suggestions"""
        return self._make_request("DataKeywordSuggestionsFetchAction", {"keyword": keyword})

    def get_link_metrics(self, url: str) -> Dict[str, Any]:
        """Get link metrics for a URL"""
        return self._make_request("DataLinkMetricsFetchAction", {"targets": [url]})

# Global instance
moz_api = MozAPI()

def get_domain_overview(domain: str) -> Dict[str, Any]:
    """Get domain overview metrics"""
    return moz_api.get_domain_overview(domain)

def get_keyword_difficulty(term: str) -> Dict[str, Any]:
    """Get keyword difficulty metrics"""
    return moz_api.get_keyword_difficulty(term)

def get_keyword_suggestions(keyword: str) -> Dict[str, Any]:
    """Get keyword suggestions"""
    return moz_api.get_keyword_suggestions(keyword)

def get_link_metrics(url: str) -> Dict[str, Any]:
    """Get link metrics for a URL"""
    return moz_api.get_link_metrics(url)
