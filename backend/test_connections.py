#!/usr/bin/env python3
"""
Test script to verify database connections to Neon PostgreSQL and Qdrant
"""

import asyncio
import sys
from sqlalchemy import text
from backend.database import engine
from backend.services.qdrant import qdrant_service
from backend.services.tasks import task_service
from backend.settings import settings

def test_neon_postgresql():
    """Test connection to Neon PostgreSQL"""
    print("Testing Neon PostgreSQL connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"OK Connected to Neon PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"FAIL Failed to connect to Neon PostgreSQL: {e}")
        return False

def test_qdrant():
    """Test connection to Qdrant"""
    print("Testing Qdrant connection...")
    try:
        # Try to get collection info
        info = qdrant_service.get_collection_info()
        print(f"✅ Connected to Qdrant: {info}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        return False

def test_embedding_service():
    """Test embedding service"""
    print("Testing embedding service...")
    try:
        from backend.services.embeddings import embedding_service

        # Test embedding generation
        text = "Test task for embedding"
        embedding = embedding_service.generate_embedding(text)
        print(f"✅ Generated embedding of size: {len(embedding)}")
        return True
    except Exception as e:
        print(f"❌ Failed to test embedding service: {e}")
        return False

def test_task_service():
    """Test task service initialization"""
    print("Testing task service...")
    try:
        # This will also test Qdrant collection creation
        collection_info = task_service.get_collection_info()
        print(f"✅ Task service initialized: {collection_info}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize task service: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔍 Testing database connections...\n")

    tests = [
        ("Neon PostgreSQL", test_neon_postgresql),
        ("Qdrant", test_qdrant),
        ("Embedding Service", test_embedding_service),
        ("Task Service", test_task_service),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("="*50)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n🎉 All tests passed! Database connections are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check your database configuration.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)