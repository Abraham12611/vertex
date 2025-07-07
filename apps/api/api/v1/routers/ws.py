from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import aioredis

router = APIRouter()

@router.websocket("/ws/flows/{flow_id}")
async def flow_ws(websocket: WebSocket, flow_id: str):
    await websocket.accept()
    redis = await aioredis.create_redis_pool("redis://localhost:6379/0")
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"flow:{flow_id}")
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=10)
            if msg:
                await websocket.send_text(msg["data"].decode())
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"flow:{flow_id}")
        redis.close()
        await redis.wait_closed()
