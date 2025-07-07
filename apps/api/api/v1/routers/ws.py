from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, List, Optional
from uuid import UUID
import json
import asyncio
import aioredis
from datetime import datetime

from api.v1.deps import get_current_user_ws
from db.base import SessionLocal
from db.models.user import User
from db.models.task import Task

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, channel: str, user_id: str = None):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

        if user_id:
            self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, channel: str, user_id: str = None):
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]

        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

    async def broadcast_to_channel(self, message: str, channel: str):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[channel].remove(connection)

manager = ConnectionManager()

# WebSocket authentication helper
async def get_current_user_ws(websocket: WebSocket) -> Optional[User]:
    """Get current user from WebSocket connection."""
    try:
        # Extract token from query parameters or headers
        token = websocket.query_params.get("token")
        if not token:
            return None

        # Verify token (simplified for demo)
        from core.security import decode_access_token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id:
            async with SessionLocal() as session:
                user = await session.get(User, user_id)
                return user
    except:
        pass
    return None

# WebSocket endpoints
@router.websocket("/ws/flows/{flow_id}")
async def flow_websocket(
    websocket: WebSocket,
    flow_id: str,
    user: User = Depends(get_current_user_ws)
):
    """WebSocket for real-time flow updates."""
    if not user:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await manager.connect(websocket, f"flow:{flow_id}", str(user.id))

    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "flow_id": flow_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to flow updates"
        }))

        # Connect to Redis for real-time updates
        redis = await aioredis.create_redis_pool("redis://localhost:6379/0")
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"flow:{flow_id}")

        # Send flow status
        async with SessionLocal() as session:
            flow = await session.get(Task, flow_id)
            if flow:
                await websocket.send_text(json.dumps({
                    "type": "flow_status",
                    "flow_id": flow_id,
                    "status": flow.status,
                    "progress": 0,  # Would calculate based on subtasks
                    "timestamp": datetime.now().isoformat()
                }))

        while True:
            # Check for Redis messages
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if msg:
                await websocket.send_text(msg["data"].decode())

            # Check for client messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))

            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"flow:{flow_id}", str(user.id))
    finally:
        if 'redis' in locals():
            await pubsub.unsubscribe(f"flow:{flow_id}")
            redis.close()
            await redis.wait_closed()

@router.websocket("/ws/agents/{agent_id}")
async def agent_websocket(
    websocket: WebSocket,
    agent_id: str,
    user: User = Depends(get_current_user_ws)
):
    """WebSocket for real-time agent updates."""
    if not user:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await manager.connect(websocket, f"agent:{agent_id}", str(user.id))

    try:
        await websocket.send_text(json.dumps({
            "type": "connection",
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to agent updates"
        }))

        redis = await aioredis.create_redis_pool("redis://localhost:6379/0")
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"agent:{agent_id}")

        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if msg:
                await websocket.send_text(msg["data"].decode())

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"agent:{agent_id}", str(user.id))

@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    user: User = Depends(get_current_user_ws)
):
    """WebSocket for user notifications."""
    if not user:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await manager.connect(websocket, f"notifications:{user.id}", str(user.id))

    try:
        await websocket.send_text(json.dumps({
            "type": "connection",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to notifications"
        }))

        redis = await aioredis.create_redis_pool("redis://localhost:6379/0")
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"notifications:{user.id}")

        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if msg:
                await websocket.send_text(msg["data"].decode())

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"notifications:{user.id}", str(user.id))

@router.websocket("/ws/analytics")
async def analytics_websocket(
    websocket: WebSocket,
    user: User = Depends(get_current_user_ws)
):
    """WebSocket for real-time analytics updates."""
    if not user:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await manager.connect(websocket, f"analytics:{user.id}", str(user.id))

    try:
        await websocket.send_text(json.dumps({
            "type": "connection",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to analytics updates"
        }))

        # Send initial analytics data
        await websocket.send_text(json.dumps({
            "type": "analytics_update",
            "data": {
                "total_flows": 42,
                "success_rate": 0.95,
                "avg_execution_time": 2.3
            },
            "timestamp": datetime.now().isoformat()
        }))

        # Simulate real-time updates
        while True:
            await asyncio.sleep(30)  # Update every 30 seconds
            await websocket.send_text(json.dumps({
                "type": "analytics_update",
                "data": {
                    "total_flows": 42 + (datetime.now().second % 10),
                    "success_rate": 0.95,
                    "avg_execution_time": 2.3
                },
                "timestamp": datetime.now().isoformat()
            }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"analytics:{user.id}", str(user.id))

# WebSocket utility endpoints
@router.post("/ws/broadcast/{channel}")
async def broadcast_message(
    channel: str,
    message: dict,
    user: User = Depends(get_current_user_ws)
):
    """Broadcast message to a specific channel."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await manager.broadcast_to_channel(
        json.dumps({
            "type": "broadcast",
            "channel": channel,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }),
        channel
    )

    return {"message": "Broadcast sent successfully"}

@router.get("/ws/connections")
async def get_active_connections(
    user: User = Depends(get_current_user_ws)
):
    """Get active WebSocket connections."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {
        "active_channels": len(manager.active_connections),
        "user_connections": len(manager.user_connections),
        "channels": list(manager.active_connections.keys())
    }
