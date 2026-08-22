#!/usr/bin/env python3
"""
Тесты для API сервера
Запуск: python test_api.py
"""

import httpx
import asyncio
import sys

async def test_api():
    """Запускает все тесты"""
    print("🚀 Testing server...")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Проверяем, что сервер отвечает
        print("📡 Testing GET /...")
        resp = await client.get(f"{base_url}/")
        print(f"   GET / -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        # 2. Проверяем статику
        print("📡 Testing GET /style.css...")
        resp = await client.get(f"{base_url}/style.css")
        print(f"   GET /style.css -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        # 3. Проверяем main.js
        print("📡 Testing GET /main.js...")
        resp = await client.get(f"{base_url}/main.js")
        print(f"   GET /main.js -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        # 4. Проверяем регистрацию
        print("📡 Testing POST /auth/register-new...")
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        resp = await client.post(
            f"{base_url}/auth/register-new",
            json=payload
        )
        print(f"   POST /auth/register-new -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        token = data.get("access_token")
        assert token is not None, "No access_token in response"
        print(f"   ✅ Token received: {token[:20]}...")
        
        # 5. Проверяем /auth/me с токеном
        print("📡 Testing GET /auth/me...")
        resp = await client.get(
            f"{base_url}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   GET /auth/me -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data["username"] == "testuser", f"Expected 'testuser', got {data['username']}"
        print(f"   ✅ User: {data}")
        
        # 6. Проверяем вход
        print("📡 Testing POST /auth/login...")
        resp = await client.post(
            f"{base_url}/auth/login",
            data={"username": "testuser", "password": "testpass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   POST /auth/login -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        token2 = data.get("access_token")
        assert token2 is not None, "No access_token in response"
        print(f"   ✅ Login successful")
        
        print("\n✅ ALL TESTS PASSED!")
        return True

async def main():
    try:
        success = await test_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
