from crewai_tools.base import BaseTool
import requests

class PgVectorSearchTool(BaseTool):
    def __init__(self, api_url, project_id):
        self.api_url = api_url
        self.project_id = project_id

    def run(self, query, top_k=3):
        resp = requests.post(
            f"{self.api_url}/search",
            json={"project_id": self.project_id, "query": query, "top_k": top_k}
        )
        return resp.json()["matches"]
