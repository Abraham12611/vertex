from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import asyncio
import aioredis
from sqlalchemy import text

from db.base import SessionLocal
from core.settings import settings

router = APIRouter()

# Pydantic models
class ServiceStatus(BaseModel):
    name: str
    status: str
    response_time: float
    last_check: datetime
    details: Dict[str, Any] = {}

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: List[ServiceStatus]
    uptime: float

# Health check functions
async def check_database() -> ServiceStatus:
    """Check database connectivity and performance."""
    start_time = datetime.now()
    try:
        async with SessionLocal() as session:
            # Test basic query
            result = await session.execute(text("SELECT 1"))
            result.scalar()

            # Test connection pool
            await session.execute(text("SELECT version()"))

            response_time = (datetime.now() - start_time).total_seconds()

            return ServiceStatus(
                name="database",
                status="healthy",
                response_time=response_time,
                last_check=datetime.now(),
                details={
                    "type": "postgresql",
                    "host": settings.POSTGRES_HOST,
                    "database": settings.POSTGRES_DB
                }
            )
    except Exception as e:
        return ServiceStatus(
            name="database",
            status="unhealthy",
            response_time=(datetime.now() - start_time).total_seconds(),
            last_check=datetime.now(),
            details={"error": str(e)}
        )

async def check_redis() -> ServiceStatus:
    """Check Redis connectivity."""
    start_time = datetime.now()
    try:
        redis = await aioredis.create_redis_pool("redis://localhost:6379/0")
        await redis.ping()
        redis.close()
        await redis.wait_closed()

        response_time = (datetime.now() - start_time).total_seconds()

        return ServiceStatus(
            name="redis",
            status="healthy",
            response_time=response_time,
            last_check=datetime.now(),
            details={"type": "redis", "host": "localhost", "port": 6379}
        )
    except Exception as e:
        return ServiceStatus(
            name="redis",
            status="unhealthy",
            response_time=(datetime.now() - start_time).total_seconds(),
            last_check=datetime.now(),
            details={"error": str(e)}
        )

async def check_embeddings() -> ServiceStatus:
    """Check embedding service."""
    start_time = datetime.now()
    try:
        from core.embeddings import embed
        # Test embedding generation
        test_text = ["test"]
        embeddings = await embed(test_text)

        response_time = (datetime.now() - start_time).total_seconds()

        return ServiceStatus(
            name="embeddings",
            status="healthy",
            response_time=response_time,
            last_check=datetime.now(),
            details={
                "model": "sentence-transformers",
                "dimensions": len(embeddings[0]) if embeddings else 0
            }
        )
    except Exception as e:
        return ServiceStatus(
            name="embeddings",
            status="unhealthy",
            response_time=(datetime.now() - start_time).total_seconds(),
            last_check=datetime.now(),
            details={"error": str(e)}
        )

async def check_llm() -> ServiceStatus:
    """Check LLM service (Groq)."""
    start_time = datetime.now()
    try:
        from core.llm import get_llm
        llm = get_llm()
        # Test simple completion
        response = await llm.ainvoke("Hello")

        response_time = (datetime.now() - start_time).total_seconds()

        return ServiceStatus(
            name="llm",
            status="healthy",
            response_time=response_time,
            last_check=datetime.now(),
            details={
                "provider": "groq",
                "model": "llama3-8b-8192"
            }
        )
    except Exception as e:
        return ServiceStatus(
            name="llm",
            status="unhealthy",
            response_time=(datetime.now() - start_time).total_seconds(),
            last_check=datetime.now(),
            details={"error": str(e)}
        )

async def check_external_apis() -> ServiceStatus:
    """Check external API connectivity."""
    start_time = datetime.now()
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            # Test Moz API (if configured)
            if hasattr(settings, 'MOZ_API_KEY') and settings.MOZ_API_KEY:
                response = await client.get(
                    "https://moz.com/api/v2/domain_authority",
                    params={"domains": "example.com"},
                    headers={"Authorization": f"Bearer {settings.MOZ_API_KEY}"},
                    timeout=5.0
                )
                moz_status = "healthy" if response.status_code == 200 else "unhealthy"
            else:
                moz_status = "not_configured"

        response_time = (datetime.now() - start_time).total_seconds()

        return ServiceStatus(
            name="external_apis",
            status="healthy" if moz_status == "healthy" else "partial",
            response_time=response_time,
            last_check=datetime.now(),
            details={
                "moz_api": moz_status,
                "coral_protocol": "not_configured"  # Would need Coral integration
            }
        )
    except Exception as e:
        return ServiceStatus(
            name="external_apis",
            status="unhealthy",
            response_time=(datetime.now() - start_time).total_seconds(),
            last_check=datetime.now(),
            details={"error": str(e)}
        )

# Health check endpoints
@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all services."""
    start_time = datetime.now()

    # Run all health checks concurrently
    checks = await asyncio.gather(
        check_database(),
        check_redis(),
        check_embeddings(),
        check_llm(),
        check_external_apis(),
        return_exceptions=True
    )

    # Process results
    services = []
    overall_status = "healthy"

    for check in checks:
        if isinstance(check, Exception):
            services.append(ServiceStatus(
                name="unknown",
                status="error",
                response_time=0.0,
                last_check=datetime.now(),
                details={"error": str(check)}
            ))
            overall_status = "unhealthy"
        else:
            services.append(check)
            if check.status != "healthy":
                overall_status = "unhealthy"

    total_time = (datetime.now() - start_time).total_seconds()

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        services=services,
        uptime=total_time
    )

@router.get("/simple")
async def simple_health():
    """Simple health check for load balancers."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/database")
async def database_health():
    """Database-specific health check."""
    status = await check_database()
    if status.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unhealthy: {status.details.get('error', 'Unknown error')}"
        )
    return status

@router.get("/redis")
async def redis_health():
    """Redis-specific health check."""
    status = await check_redis()
    if status.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis unhealthy: {status.details.get('error', 'Unknown error')}"
        )
    return status

@router.get("/embeddings")
async def embeddings_health():
    """Embeddings service health check."""
    status = await check_embeddings()
    if status.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embeddings service unhealthy: {status.details.get('error', 'Unknown error')}"
        )
    return status

@router.get("/llm")
async def llm_health():
    """LLM service health check."""
    status = await check_llm()
    if status.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service unhealthy: {status.details.get('error', 'Unknown error')}"
        )
    return status

@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    # Check critical services only
    db_status = await check_database()
    redis_status = await check_redis()

    if db_status.status != "healthy" or redis_status.status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )

    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

# System information
@router.get("/info")
async def system_info():
    """Get system information and configuration."""
    return {
        "version": "1.0.0",
        "environment": "development",  # Would be from settings
        "database": {
            "host": settings.POSTGRES_HOST,
            "database": settings.POSTGRES_DB,
            "ssl_mode": getattr(settings, 'POSTGRES_SSLMODE', 'require')
        },
        "redis": {
            "host": "localhost",
            "port": 6379
        },
        "llm": {
            "provider": "groq",
            "model": "llama3-8b-8192"
        },
        "embeddings": {
            "model": "sentence-transformers",
            "dimensions": 1536
        },
        "features": {
            "pgvector": True,
            "celery": True,
            "websockets": True
        }
    }
