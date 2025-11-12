#!/usr/bin/env python3
"""
Simple Authentication Test Script
Tests all authentication endpoints using Python requests.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 50)
print("Testing Authentication Endpoints")
print("=" * 50)
print()

# Create session for cookie management
session = requests.Session()

# Test 1: Health Check
print("1. Testing Health Check...")
try:
    response = session.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   ✓ PASSED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 2: User Registration
print("2. Testing User Registration...")
try:
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123",
        "role": "student",
        "department": "Computer Science"
    }
    response = session.post(f"{BASE_URL}/auth/register", json=data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 201:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 3: Duplicate Email (should fail)
print("3. Testing Duplicate Email Registration (should fail)...")
try:
    response = session.post(f"{BASE_URL}/auth/register", json=data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 400:
        print("   ✓ PASSED (correctly rejected)\n")
    else:
        print("   ✗ FAILED (should have returned 400)\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 4: Email Availability Check
print("4. Testing Email Availability Check...")
try:
    response = session.post(f"{BASE_URL}/auth/check-email", 
                           json={"email": "test@example.com"})
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    if not result.get('available'):
        print("   ✓ PASSED (email correctly marked as unavailable)\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 5: Login
print("5. Testing Login...")
try:
    login_data = {
        "email": "test@example.com",
        "password": "TestPass123"
    }
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 6: Get Current User (authenticated)
print("6. Testing Get Current User Profile...")
try:
    response = session.get(f"{BASE_URL}/auth/me")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 7: Update Profile
print("7. Testing Update User Profile...")
try:
    update_data = {
        "name": "Updated Test User",
        "department": "Software Engineering"
    }
    response = session.patch(f"{BASE_URL}/auth/me", json=update_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 8: Change Password
print("8. Testing Change Password...")
try:
    password_data = {
        "current_password": "TestPass123",
        "new_password": "NewPass456"
    }
    response = session.post(f"{BASE_URL}/auth/change-password", json=password_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 9: Logout
print("9. Testing Logout...")
try:
    response = session.post(f"{BASE_URL}/auth/logout")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 10: Access protected route after logout (should fail)
print("10. Testing Protected Route After Logout (should fail)...")
try:
    response = session.get(f"{BASE_URL}/auth/me")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 401:
        print("   ✓ PASSED (correctly denied access)\n")
    else:
        print("   ✗ FAILED (should have returned 401)\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

# Test 11: Login with new password
print("11. Testing Login with New Password...")
try:
    login_data = {
        "email": "test@example.com",
        "password": "NewPass456"
    }
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✓ PASSED\n")
    else:
        print("   ✗ FAILED\n")
except Exception as e:
    print(f"   ✗ FAILED: {e}\n")

print("=" * 50)
print("Authentication Tests Complete!")
print("=" * 50)
