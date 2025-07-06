import httpx
from typing import Dict, Any, List, Optional
from core.settings import settings

class CoralClient:
    def __init__(self):
        self.base_url = settings.CORAL_SERVER_URL
        self.api_key = settings.CORAL_API_KEY

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Coral Protocol server"""
        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()
            except httpx.RequestException as e:
                raise Exception(f"Coral Protocol request failed: {str(e)}")

    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent in Coral Protocol"""
        return await self._make_request("POST", "/agents", agent_data)

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent information"""
        return await self._make_request("GET", f"/agents/{agent_id}")

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return await self._make_request("GET", "/agents")

    async def create_thread(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new communication thread"""
        return await self._make_request("POST", "/threads", thread_data)

    async def send_message(self, thread_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message in a thread"""
        return await self._make_request("POST", f"/threads/{thread_id}/messages", message_data)

    async def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a thread"""
        return await self._make_request("GET", f"/threads/{thread_id}/messages")

# Global instance
coral_client = CoralClient()

async def create_devrel_agent(name: str, role: str, capabilities: List[str]) -> Dict[str, Any]:
    """Create a DevRel agent in Coral Protocol"""
    agent_data = {
        "name": name,
        "role": role,
        "capabilities": capabilities,
        "type": "devrel",
        "metadata": {
            "platform": "vertex",
            "version": "1.0.0"
        }
    }
    return await coral_client.create_agent(agent_data)

async def create_content_thread(project_id: str, content_type: str) -> Dict[str, Any]:
    """Create a content creation thread"""
    thread_data = {
        "project_id": project_id,
        "type": "content_creation",
        "content_type": content_type,
        "metadata": {
            "platform": "vertex",
            "workflow": "devrel_content"
        }
    }
    return await coral_client.create_thread(thread_data)

async def send_content_message(thread_id: str, content: str, message_type: str = "content_request") -> Dict[str, Any]:
    """Send a content-related message"""
    message_data = {
        "content": content,
        "type": message_type,
        "metadata": {
            "platform": "vertex",
            "timestamp": "now"
        }
    }
    return await coral_client.send_message(thread_id, message_data)