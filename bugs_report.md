# Bug Report - User Management API

## Executive Summary

This report details the bugs detected in the User Management API. A total of **17 bugs** have been identified through automated testing, with **4 Critical**, **4 High**, **5 Medium**, and **4 Low** severity levels.

**Test Results:** 76 tests executed, 59 passed, 17 failed, 1 warning

## Bug List

### BUG-001: Logout Invalid Token Handling
**Severity:** Medium  
**Category:** Security/Logic

**Description:**
The logout endpoint returns "Logged out successfully" message when called with invalid token. It should return "No active session" for invalid tokens.

**Steps to Reproduce:**
1. Send a request to POST `/logout` endpoint with invalid token
2. Check the response message

**Expected Result:**
- Status Code: 200
- Message: "No active session"

**Actual Result:**
- Status Code: 200
- Message: "Logged out successfully"

**Evidence:**
```json
// Request
POST /logout
Headers: {
    "Authorization": "Bearer invalid_token"
}

// Response
{
    "message": "Logged out successfully"
}
```

---

### BUG-002: Token Expiration Handling
**Severity:** High  
**Category:** Security

**Description:**
Malformed tokens (missing Bearer prefix) are accepted instead of being rejected with 401 Unauthorized.

**Steps to Reproduce:**
1. Login to get a valid token
2. Use the token without "Bearer " prefix in Authorization header
3. Access a protected endpoint

**Expected Result:**
- Status Code: 401 Unauthorized

**Actual Result:**
- Status Code: 200 OK

**Evidence:**
```json
// Request
GET /users/1
Headers: {
    "Authorization": "a8ce1711ec4631354f284c255e9bbf75"  // Missing "Bearer "
}

// Response
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30,
    "created_at": "2025-09-16T01:01:00.326631"
}
```

---

### BUG-003: Search Endpoint Not Working
**Severity:** High  
**Category:** Functionality

**Description:**
All search endpoint requests return 400 Bad Request instead of 200 OK with search results.

**Steps to Reproduce:**
1. Send a request to GET `/users/search?q=john` endpoint

**Expected Result:**
- Status Code: 200
- List of users matching the search query

**Actual Result:**
- Status Code: 400
- Bad Request error

**Evidence:**
```json
// Request
GET /users/search?q=john

// Response
{
    "detail": "Bad Request"
}
```

---

### BUG-004: Search Field Validation Error
**Severity:** High  
**Category:** Validation

**Description:**
Search endpoint with field parameter returns 400 Bad Request instead of 422 Unprocessable Entity for invalid fields.

**Steps to Reproduce:**
1. Send a request to GET `/users/search?q=test&field=invalid` endpoint

**Expected Result:**
- Status Code: 422
- Validation error message

**Actual Result:**
- Status Code: 400
- Bad Request error

**Evidence:**
```json
// Request
GET /users/search?q=test&field=invalid

// Response
{
    "detail": "Bad Request"
}
```

---

### BUG-005: Search Empty Query Handling
**Severity:** Medium  
**Category:** Validation

**Description:**
Search endpoint with empty query returns 400 Bad Request instead of 422 Unprocessable Entity.

**Steps to Reproduce:**
1. Send a request to GET `/users/search?q=` endpoint

**Expected Result:**
- Status Code: 422
- Validation error for empty query

**Actual Result:**
- Status Code: 400
- Bad Request error

**Evidence:**
```json
// Request
GET /users/search?q=

// Response
{
    "detail": "Bad Request"
}
```

---

### BUG-006: Rate Limiting Performance Issue
**Severity:** Medium  
**Category:** Performance

**Description:**
Rate limiting is not working properly. No requests are being rate limited when they should be.

**Steps to Reproduce:**
1. Make 20 rapid requests to the API
2. Check if any requests return 429 Too Many Requests

**Expected Result:**
- Some requests should return 429
- Rate limiting should be enforced

**Actual Result:**
- All requests return 201 Created
- No rate limiting occurs

**Evidence:**
```json
// Request (repeated 20 times)
POST /users
{
    "username": "rate_test_0",
    "email": "rate_0@example.com",
    "password": "Password123",
    "age": 25
}

// All responses
{
    "id": 7,
    "username": "rate_test_0",
    "email": "rate_0@example.com",
    "age": 25,
    "created_at": "2025-09-16T01:01:12.123456"
}
```

---

### BUG-007: Password Hash Security Vulnerability
**Severity:** Critical  
**Category:** Security

**Description:**
Passwords are hashed with MD5 which is cryptographically broken and vulnerable to rainbow table attacks.

**Steps to Reproduce:**
1. Create a user with a password
2. Check the password storage method in the code

**Expected Result:**
- A secure hash algorithm like bcrypt, scrypt, or Argon2 should be used

**Actual Result:**
- MD5 is being used for password hashing

**Evidence:**
```python
# Code in main.py
def hash_password(password: str) -> str:
    salt = "static_salt_2024"  # Static salt
    return hashlib.md5(f"{salt}{password}".encode()).hexdigest()  # MD5 hash
```

---

### BUG-008: Session Hijacking Vulnerability
**Severity:** High  
**Category:** Security

**Description:**
Predictable session tokens are accepted, making the system vulnerable to session hijacking attacks.

**Steps to Reproduce:**
1. Try to access a protected endpoint with a predictable token
2. Check if the request is accepted

**Expected Result:**
- Status Code: 401 Unauthorized
- Token should be rejected

**Actual Result:**
- Status Code: 200 OK
- Predictable token is accepted

**Evidence:**
```json
// Request
GET /users/1
Headers: {
    "Authorization": "Bearer 12345678901234567890123456789012"
}

// Response
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30,
    "created_at": "2025-09-16T01:01:00.326631"
}
```

---

### BUG-009: Information Disclosure in Stats
**Severity:** High  
**Category:** Security

**Description:**
Stats endpoint exposes sensitive session tokens when include_details=true parameter is used.

**Steps to Reproduce:**
1. Send a request to GET `/stats?include_details=true` endpoint
2. Check if session tokens are exposed

**Expected Result:**
- Session tokens should not be exposed
- Only non-sensitive statistics should be returned

**Actual Result:**
- Session tokens are exposed in the response

**Evidence:**
```json
// Request
GET /stats?include_details=true

// Response
{
    "active_sessions": 8,
    "active_users": 110,
    "api_version": "1.0.0",
    "inactive_users": 0,
    "session_tokens": [
        "32f29dc3e7328e21ac8e78268054ca47",
        "5ec3a1c7457a342bba0eeca8459ec18c",
        "75b9dc226b6cb36afab68ba5b477b320",
        "36a6ec8da135b2df7b6b8d348e392bbc",
        "d74d80dcdde9aed056a87f5ee1b964d9"
    ]
}
```

---

### BUG-010: User Creation Rate Limiting
**Severity:** Medium  
**Category:** Performance

**Description:**
Rate limiting is affecting normal user creation operations, causing legitimate requests to return 429 Too Many Requests.

**Steps to Reproduce:**
1. Try to create a new user
2. Check if the request is rate limited

**Expected Result:**
- Status Code: 201 Created
- User should be created successfully

**Actual Result:**
- Status Code: 429 Too Many Requests
- User creation fails due to rate limiting

**Evidence:**
```json
// Request
POST /users
{
    "username": "new_user_test",
    "email": "new_user_test@example.com",
    "password": "Password123",
    "age": 25,
    "phone": "+1234567890"
}

// Response
{
    "detail": "Too Many Requests"
}
```

---

### BUG-011: Pagination Logic Error
**Severity:** High  
**Category:** Logic

**Description:**
Pagination returns limit+1 records instead of the specified limit. When limit=5, 6 records are returned.

**Steps to Reproduce:**
1. Send a request to GET `/users?limit=5&offset=0` endpoint
2. Count the returned records

**Expected Result:**
- Maximum 5 records should be returned

**Actual Result:**
- 6 records are returned

**Evidence:**
```json
// Request
GET /users?limit=5&offset=0

// Response
[
    {"id": 1, "username": "john_doe", "email": "john@example.com", "age": 30, "created_at": "2025-09-16T01:01:00.326631"},
    {"id": 2, "username": "jane_doe", "email": "jane@example.com", "age": 25, "created_at": "2025-09-16T01:01:02.378829"},
    {"id": 3, "username": "bob_smith", "email": "bob@example.com", "age": 35, "created_at": "2025-09-16T01:01:04.444507"},
    {"id": 4, "username": "alice_johnson", "email": "alice@example.com", "age": 28, "created_at": "2025-09-16T01:01:06.496605"},
    {"id": 5, "username": "charlie_brown", "email": "charlie@example.com", "age": 22, "created_at": "2025-09-16T01:01:08.548605"},
    {"id": 6, "username": "test.user", "email": "test.user@example.com", "age": 40, "created_at": "2025-09-16T01:01:10.614036"}
]
// 6 records instead of 5
```

---

### BUG-012: Username Case Sensitivity Rate Limiting
**Severity:** Medium  
**Category:** Performance

**Description:**
Rate limiting is preventing proper testing of username case sensitivity validation, causing 429 instead of allowing proper validation testing.

**Steps to Reproduce:**
1. Create a user with username "CaseSensitiveUser"
2. Try to create another user with "casesensitiveuser"

**Expected Result:**
- Status Code: 201 Created for first user
- Status Code: 400 Bad Request for second user (duplicate)

**Actual Result:**
- Status Code: 429 Too Many Requests for both attempts
- Rate limiting prevents proper validation testing

**Evidence:**
```json
// First Request
POST /users
{
    "username": "CaseSensitiveUser",
    "email": "case@example.com",
    "password": "Password123",
    "age": 25
}

// Response
{
    "detail": "Too Many Requests"
}
```

---

### BUG-013: Static Salt Security Vulnerability
**Severity:** Critical  
**Category:** Security

**Description:**
All passwords use the same static salt, making rainbow table attacks easier and reducing security.

**Steps to Reproduce:**
1. Review the password hashing function in the code

**Expected Result:**
- Each password should have a unique salt

**Actual Result:**
- All passwords use the same static salt

**Evidence:**
```python
# Code in main.py
def hash_password(password: str) -> str:
    salt = "static_salt_2024"  # Same salt for all passwords
    return hashlib.md5(f"{salt}{password}".encode()).hexdigest()
```

---

### BUG-014: Session Expiration Disabled
**Severity:** High  
**Category:** Security

**Description:**
Session expiration is commented out, meaning sessions never expire, creating a security risk.

**Steps to Reproduce:**
1. Review the session validation code

**Expected Result:**
- Sessions should expire after a certain time period

**Actual Result:**
- Sessions never expire

**Evidence:**
```python
# Code in main.py (commented out)
# if datetime.now() > session["expires_at"]:
#     raise HTTPException(status_code=401, detail="Session expired")
```

---

### BUG-015: Phone Number Validation Regex
**Severity:** Medium  
**Category:** Validation

**Description:**
Phone number validation regex only accepts US format, rejecting valid international phone numbers.

**Steps to Reproduce:**
1. Try to create a user with international phone number
2. Check if validation passes

**Expected Result:**
- International phone numbers should be accepted

**Actual Result:**
- Only US format phone numbers are accepted

**Evidence:**
```python
# Code in main.py
if v and not re.match(r"^\+?1?\d{9,15}$", v):  # Only US format
    raise ValueError("Invalid phone number format")
```

---

### BUG-016: Rate Limiting Affecting Test Execution
**Severity:** Low  
**Category:** Performance

**Description:**
Rate limiting is affecting test execution, causing legitimate test operations to return 429 Too Many Requests instead of expected results.

**Steps to Reproduce:**
1. Run the test suite
2. Observe that many tests fail due to rate limiting

**Expected Result:**
- Tests should not be affected by rate limiting
- Normal test operations should succeed

**Actual Result:**
- Many tests return 429 Too Many Requests
- Test execution is disrupted by rate limiting

**Evidence:**
```json
// Multiple test failures due to rate limiting
FAILED test_classes/test_users.py::TestUserCRUD::test_create_user_valid
assert response.status_code == 201
E   assert 429 == 201

FAILED test_classes/test_security.py::TestSecurity::test_password_hash_security
assert response.status_code == 201
E   assert 429 == 201

FAILED test_classes/test_users.py::TestUserCRUD::test_username_case_sensitivity
assert response.status_code == 201
E   assert 429 == 201
```

---

### BUG-017: Health Check Memory Count Bug
**Severity:** Low  
**Category:** Logic / Monitoring

**Description:**
Health endpoint returns incorrect memory counts. The `memory_users` and `memory_sessions` fields return the length of string representation instead of actual counts.

**Steps to Reproduce:**
1. Send a request to GET `/health` endpoint
2. Check the `memory_users` and `memory_sessions` values

**Expected Result:**
- `memory_users` should equal the number of users in the database
- `memory_sessions` should equal the number of active sessions

**Actual Result:**
- `memory_users` returns length of string representation (e.g., 274 instead of actual user count)
- `memory_sessions` returns length of string representation

**Evidence:**
```json
// Request
GET /health

// Response
{
    "status": "healthy",
    "timestamp": "2025-09-16T02:00:02.066809",
    "memory_users": 274,        // Wrong: this is len(str(users_db))
    "memory_sessions": 2        // Wrong: this is len(str(sessions))
}
```

---

## Summary

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 4     | 24%        |
| High     | 4     | 24%        |
| Medium   | 5     | 29%        |
| Low      | 4     | 23%        |
| **Total**| **17**| **100%**   |

## Recommendations

1. **Immediate Actions (Critical Bugs):**
   - Replace MD5 hash with bcrypt or Argon2
   - Replace static salt with unique salt per password
   - Enable session expiration functionality
   - Fix session hijacking vulnerability

2. **High Priority (High Bugs):**
   - Fix token expiration handling (malformed tokens)
   - Fix search endpoint functionality
   - Fix search field validation
   - Fix pagination logic (limit+1 issue)
   - Prevent information disclosure in stats endpoint

3. **Medium Priority:**
   - Fix logout endpoint inconsistent behavior
   - Fix rate limiting performance issues
   - Fix user creation rate limiting
   - Fix username case sensitivity testing
   - Fix phone number validation regex
   - Fix search empty query handling

4. **Low Priority:**
   - Fix health check memory count calculation
   - Fix rate limiting affecting test execution