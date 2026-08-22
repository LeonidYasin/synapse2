#!/usr/bin/env python3
"""
Тесты для сервера. Запускается в GitHub Actions.
"""

import httpx
import asyncio
import json
import sys

async def test():
    print('🚀 Testing server...')
    all_passed = True
    token = None

    async with httpx.AsyncClient() as client:
        # 1. GET /
        print('📡 Testing GET /...')
        resp = await client.get('http://localhost:8000/')
        print(f'   GET / -> {resp.status_code}')
        if resp.status_code != 200:
            all_passed = False
            print('   ❌ FAILED')
        else:
            print('   ✅ PASSED')

        # 2. GET /style.css
        print('📡 Testing GET /style.css...')
        resp = await client.get('http://localhost:8000/style.css')
        print(f'   GET /style.css -> {resp.status_code}')
        if resp.status_code != 200:
            all_passed = False
            print('   ❌ FAILED')
        else:
            print('   ✅ PASSED')

        # 3. GET /main.js
        print('📡 Testing GET /main.js...')
        resp = await client.get('http://localhost:8000/main.js')
        print(f'   GET /main.js -> {resp.status_code}')
        if resp.status_code != 200:
            all_passed = False
            print('   ❌ FAILED')
        else:
            print('   ✅ PASSED')

        # 4. POST /auth/register-new
        print('📡 Testing POST /auth/register-new...')
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        resp = await client.post(
            'http://localhost:8000/auth/register-new',
            json=payload
        )
        print(f'   POST /auth/register-new -> {resp.status_code}')
        if resp.status_code != 200:
            all_passed = False
            print('   ❌ FAILED')
            print(f'   Response: {resp.text}')
        else:
            data = resp.json()
            token = data.get('access_token')
            if token:
                print(f'   ✅ Token received: {token[:20]}...')
                print('   ✅ PASSED')
            else:
                all_passed = False
                print('   ❌ No token in response')

        # 5. GET /auth/me
        if token:
            print('📡 Testing GET /auth/me...')
            resp = await client.get(
                'http://localhost:8000/auth/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            print(f'   GET /auth/me -> {resp.status_code}')
            if resp.status_code == 200:
                data = resp.json()
                print(f'   User: {data}')
                if data.get('username') == 'testuser':
                    print('   ✅ PASSED')
                else:
                    all_passed = False
                    print('   ❌ Wrong username')
            else:
                all_passed = False
                print('   ❌ FAILED')

        # 6. POST /auth/login
        print('📡 Testing POST /auth/login...')
        resp = await client.post(
            'http://localhost:8000/auth/login',
            data={'username': 'testuser', 'password': 'testpass123'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f'   POST /auth/login -> {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            if data.get('access_token'):
                print('   ✅ PASSED')
            else:
                all_passed = False
                print('   ❌ No token')
        else:
            all_passed = False
            print('   ❌ FAILED')

    print('')
    print('=' * 50)
    if all_passed:
        print('✅ ALL TESTS PASSED!')
        sys.exit(0)
    else:
        print('❌ SOME TESTS FAILED!')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(test())
