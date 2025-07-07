import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_register_login_and_protected():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register
        r = await ac.post("/auth/register", json={"email": "test@vertex.com", "password": "testpass"})
        assert r.status_code == 200
        # Login
        r = await ac.post("/auth/login", json={"email": "test@vertex.com", "password": "testpass"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        # Protected route
        r = await ac.get("/prompts", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        # Unauthorized
        r = await ac.get("/prompts")
        assert r.status_code == 401
