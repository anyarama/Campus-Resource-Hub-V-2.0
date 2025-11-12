#!/bin/bash
# Test Authentication Endpoints
# Tests registration, login, profile access, and logout

echo "=========================================="
echo "Testing Authentication Flow"
echo "=========================================="
echo ""

BASE_URL="http://localhost:5000/api"

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s -X GET "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

# Test 2: Register a new user
echo "2. Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123",
    "role": "student",
    "department": "Computer Science"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo -e "\n"

# Test 3: Try to register with same email (should fail)
echo "3. Testing Duplicate Email Registration (should fail)..."
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another User",
    "email": "test@example.com",
    "password": "TestPass123"
  }' | python3 -m json.tool
echo -e "\n"

# Test 4: Check email availability
echo "4. Testing Email Availability Check..."
curl -s -X POST "$BASE_URL/auth/check-email" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' | python3 -m json.tool
echo -e "\n"

# Test 5: Login with correct credentials
echo "5. Testing Login with Valid Credentials..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "remember_me": false
  }')
echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo -e "\n"

# Test 6: Login with wrong password (should fail)
echo "6. Testing Login with Invalid Password (should fail)..."
curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword123"
  }' | python3 -m json.tool
echo -e "\n"

# Test 7: Get current user profile (authenticated)
echo "7. Testing Get Current User Profile (authenticated)..."
curl -s -X GET "$BASE_URL/auth/me" \
  -H "Content-Type: application/json" \
  -b cookies.txt | python3 -m json.tool
echo -e "\n"

# Test 8: Update user profile
echo "8. Testing Update User Profile..."
curl -s -X PATCH "$BASE_URL/auth/me" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Updated Test User",
    "department": "Software Engineering"
  }' | python3 -m json.tool
echo -e "\n"

# Test 9: Change password
echo "9. Testing Change Password..."
curl -s -X POST "$BASE_URL/auth/change-password" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "current_password": "TestPass123",
    "new_password": "NewPass456"
  }' | python3 -m json.tool
echo -e "\n"

# Test 10: Logout
echo "10. Testing Logout..."
curl -s -X POST "$BASE_URL/auth/logout" \
  -H "Content-Type: application/json" \
  -b cookies.txt | python3 -m json.tool
echo -e "\n"

# Test 11: Try to access protected route after logout (should fail)
echo "11. Testing Protected Route After Logout (should fail)..."
curl -s -X GET "$BASE_URL/auth/me" \
  -H "Content-Type: application/json" \
  -b cookies.txt | python3 -m json.tool
echo -e "\n"

# Test 12: Login with new password
echo "12. Testing Login with New Password..."
curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "NewPass456"
  }' | python3 -m json.tool
echo -e "\n"

# Cleanup
rm -f cookies.txt

echo "=========================================="
echo "Authentication Tests Complete!"
echo "=========================================="
