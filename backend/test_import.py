#!/usr/bin/env python3
"""
Простой тест для проверки импорта модулей и синтаксиса.
Не требует запуска сервера.
"""

print("🔍 Testing imports...")

try:
    import app.main
    print("✅ app.main imported")
except Exception as e:
    print(f"❌ app.main failed: {e}")
    exit(1)

try:
    import app.routers.auth
    print("✅ app.routers.auth imported")
except Exception as e:
    print(f"❌ app.routers.auth failed: {e}")
    exit(1)

try:
    import app.models
    print("✅ app.models imported")
except Exception as e:
    print(f"❌ app.models failed: {e}")
    exit(1)

try:
    import app.database
    print("✅ app.database imported")
except Exception as e:
    print(f"❌ app.database failed: {e}")
    exit(1)

try:
    import app.auth
    print("✅ app.auth imported")
except Exception as e:
    print(f"❌ app.auth failed: {e}")
    exit(1)

print("\n✅ All imports successful!")
