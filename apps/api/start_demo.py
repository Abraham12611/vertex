#!/usr/bin/env python3
"""
Vertex DevRel Platform Demo Startup Script
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from core.settings import settings
from core.llm import generate_content, chat_completion
from core.embeddings import embed_single
from core.moz import get_domain_overview
from agents.crew import vertex_crew

async def test_groq_connection():
    """Test Groq API connection"""
    print("🔍 Testing Groq API connection...")
    try:
        response = await generate_content("Hello, this is a test message from Vertex DevRel Platform!")
        print("✅ Groq API connection successful!")
        print(f"📝 Test response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Groq API connection failed: {str(e)}")
        return False

async def test_embeddings():
    """Test embeddings functionality"""
    print("🔍 Testing embeddings...")
    try:
        embedding = embed_single("Test text for embedding generation")
        print(f"✅ Embeddings working! Vector length: {len(embedding)}")
        return True
    except Exception as e:
        print(f"❌ Embeddings failed: {str(e)}")
        return False

async def test_crew_workflow():
    """Test CrewAI workflow"""
    print("🔍 Testing CrewAI workflow...")
    try:
        result = await vertex_crew.run_devrel_workflow(
            "Create a DevRel strategy for launching a new developer tool"
        )
        print("✅ CrewAI workflow successful!")
        return True
    except Exception as e:
        print(f"❌ CrewAI workflow failed: {str(e)}")
        return False

async def test_moz_api():
    """Test Moz API (if configured)"""
    if not settings.MOZ_API_KEY:
        print("⚠️  Moz API key not configured, skipping Moz test")
        return True

    print("🔍 Testing Moz API...")
    try:
        result = get_domain_overview("example.com")
        print("✅ Moz API connection successful!")
        return True
    except Exception as e:
        print(f"❌ Moz API failed: {str(e)}")
        return False

async def main():
    """Main demo startup function"""
    print("🚀 Starting Vertex DevRel Platform Demo...")
    print("=" * 50)

    # Check environment variables
    print("📋 Checking environment variables...")
    required_vars = [
        "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
        "POSTGRES_HOST", "POSTGRES_PORT", "GROQ_API_KEY"
    ]

    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False

    print("✅ All required environment variables are set")

    # Run tests
    tests = [
        test_groq_connection(),
        test_embeddings(),
        test_crew_workflow(),
        test_moz_api()
    ]

    results = await asyncio.gather(*tests, return_exceptions=True)

    print("\n" + "=" * 50)
    print("📊 Demo Startup Results:")

    test_names = ["Groq API", "Embeddings", "CrewAI", "Moz API"]
    passed = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ {test_names[i]}: Failed - {str(result)}")
        elif result:
            print(f"✅ {test_names[i]}: Passed")
            passed += 1
        else:
            print(f"❌ {test_names[i]}: Failed")

    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! Vertex DevRel Platform is ready!")
        print("\n📚 Available endpoints:")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/health")
        print("   - Flower (Celery): http://localhost:5555")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)