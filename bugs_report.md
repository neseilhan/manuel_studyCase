# Bug Report - User Management API

## Executive Summary

This report details the bugs detected in the User Management API. A total of **18 bugs** have been identified, with **5 Critical**, **4 High**, **6 Medium**, and **3 Low** severity levels.

**Test Results:** 74 tests executed, 56 passed, 18 failed, 1 warning

## Bug List

### BUG-001: Login Endpoint Authentication Failure
**Severity:** Critical  
**Category:** Authentication/Security

**Description:**
The login endpoint returns 401 Unauthorized even with valid user credentials. Login cannot be performed with the `john_doe` user found in test data.

**Steps to Reproduce:**
1. Start the API
2. Load test data (`python seed_data.py`)
3. Send a request to POST `/login` endpoint with this payload:
```json
{
    "username": "john_doe",
    "password": "password123"
}
```

**Expected Result:**
- Status Code: 200
- Response: Token and user information

**Actual Result:**
- Status Code: 401
- Response: "Invalid username or password"

**Evidence:**
```json
// Request
POST /login
{
    "username": "john_doe",
    "password": "password123"
}

// Response
{
    "detail": "Invalid username or password"
}
```

---

### BUG-002: Username Case Sensitivity Issue
**Severity:** High  
**Category:** Logic/Validation

**Description:**
The same username can be created multiple times with different cases (uppercase/lowercase). Usernames are stored case-insensitive but duplicate checking is done case-sensitive.

**Steps to Reproduce:**
1. Create a user with username `CaseSensitiveUser`
2. Try to create the same user again with username `casesensitiveuser`

**Expected Result:**
- Second request should return 400 Bad Request
- "Username already exists" error

**Actual Result:**
- Second request returns 201 Created
- User is successfully created
  
**Evidence:**
```json
// First request - SUCCESS
POST /users
{
    "username": "CaseSensitiveUser",
    "email": "case@example.com",
    "password": "Password123",
    "age": 25
}
// Response: 201 Created

// Second request - SHOULD FAIL but SUCCEEDS
POST /users
{
    "username": "casesensitiveuser",
    "email": "case2@example.com", 
    "password": "Password123",
    "age": 25
}
// Response: 201 Created (BUG!)
```

---

### BUG-003: Pagination Logic Error
**Severity:** High  
**Category:** Logic

**Description:**
Pagination returns limit+1 records. When limit is set to 5, 6 records are returned.

**Steps to Reproduce:**
1. Send a request to GET `/users?limit=5&offset=0` endpoint

**Expected Result:**
- Maximum 5 records should be returned

**Actual Result:**
- 6 records are returned

**Evidence:**
```python
# Code in main.py line 175
paginated_users = all_users[offset : offset + limit + 1]  # BUG: +1 extra
```

---

### BUG-004: Search Endpoint Validation Error
**Severity:** High  
**Category:** Validation

**Description:**
The search endpoint returns 400 Bad Request even with valid query parameters. All search tests are failing.

**Steps to Reproduce:**
1. Send a request to GET `/users/search?q=john` endpoint

**Expected Result:**
- Status Code: 200
- User list

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

### BUG-005: Logout Token Validation Issue
**Severity:** Medium  
**Category:** Security/Logic

**Description:**
The logout endpoint returns "Logged out successfully" message when called with invalid token. It should return "No active session" for invalid tokens.

**Steps to Reproduce:**
1. Send a request to POST `/logout` endpoint with invalid token:
```
Authorization: Bearer invalid_token
```

**Expected Result:**
- "No active session" message

**Actual Result:**
- "Logged out successfully" message

**Evidence:**
```json
// Request
POST /logout
Authorization: Bearer invalid_token

// Response
{
    "message": "Logged out successfully"  // BUG: Should be "No active session"
}
```

---

### BUG-006: MD5 Hash Usage (Security Vulnerability)
**Severity:** Critical  
**Category:** Security

**Description:**
Passwords are hashed with MD5. MD5 is not secure and vulnerable to rainbow table attacks.

**Steps to Reproduce:**
1. Review API code (main.py line 68-69)

**Expected Result:**
- A secure hash algorithm like bcrypt, scrypt, or Argon2 should be used

**Actual Result:**
- MD5 is being used

**Evidence:**
```python
# Code in main.py
def hash_password(password: str) -> str:
    salt = "static_salt_2024"  # BUG: Static salt
    return hashlib.md5(f"{salt}{password}".encode()).hexdigest()  # BUG: MD5
```

---

### BUG-007: Static Salt Usage
**Severity:** Critical  
**Category:** Security

**Description:**
The same static salt is used for all passwords. This creates a security vulnerability.

**Steps to Reproduce:**
1. Review API code (main.py line 68)

**Expected Result:**
- Unique salt should be used for each password

**Actual Result:**
- "static_salt_2024" is used for all passwords

**Evidence:**
```python
# Code in main.py line 68
salt = "static_salt_2024"  # BUG: Static salt for all passwords
```

---

### BUG-008: Session Expiration Disabled
**Severity:** High  
**Category:** Security

**Description:**
Session expiration control is commented out. Sessions never expire.

**Steps to Reproduce:**
1. Review API code (main.py lines 130-131)

**Expected Result:**
- Sessions should expire after a certain time

**Actual Result:**
- Sessions never expire

**Evidence:**
```python
# Code in main.py lines 130-131
# if datetime.now() > session["expires_at"]:
#     raise HTTPException(status_code=401, detail="Session expired")
```

---

### BUG-009: Phone Number Validation Regex Error
**Severity:** Medium  
**Category:** Validation

**Description:**
Phone number validation regex is incorrect. It rejects valid phone numbers.

**Steps to Reproduce:**
1. Review API code (main.py line 40)

**Expected Result:**
- Valid phone numbers should be accepted

**Actual Result:**
- Regex is incorrect, valid numbers are rejected

**Evidence:**
```python
# Code in main.py line 40
if v and not re.match(r"^\+?1?\d{9,15}$", v):  # BUG: Only US format
```

---

### BUG-010: Username Validation Allows Dangerous Characters
**Severity:** Medium  
**Category:** Security/Validation

**Description:**
Username validation allows dangerous characters (', ", ;).

**Steps to Reproduce:**
1. Review API code (main.py line 34)

**Expected Result:**
- Only safe characters should be allowed

**Actual Result:**
- Dangerous characters are allowed

**Evidence:**
```python
# Code in main.py line 34
if not re.match(r'^[a-zA-Z0-9_\-\'";]+$', v):  # BUG: Allows ', ", ;
```

---

### BUG-011: User ID Type Inconsistency
**Severity:** Medium  
**Category:** Logic

**Description:**
User ID is sometimes processed as string, sometimes as integer. get_user endpoint accepts string but other endpoints expect integer.

**Steps to Reproduce:**
1. Review API code (main.py lines 179-186 vs 193-196)

**Expected Result:**
- Consistent type should be used across all endpoints

**Actual Result:**
- Type inconsistency exists

**Evidence:**
```python
# get_user endpoint (line 180)
def get_user(user_id: str):  # String parameter

# update_user endpoint (line 195)  
def update_user(user_id: int, ...):  # Integer parameter
```

---

### BUG-012: Rate Limiting Logic Flaw
**Severity:** Low  
**Category:** Logic

**Description:**
Rate limiting time window calculation is incorrect. Counter does not reset after 60 seconds.

**Steps to Reproduce:**
1. Review API code (main.py lines 72-88)

**Expected Result:**
- Counter should reset after 60 seconds

**Actual Result:**
- Counter reset logic is incorrect

**Evidence:**
```python
# Code in main.py lines 77-82
if time_diff < 60:  # 1 minute window
    request_counts[ip] += 1
    if request_counts[ip] > 100:  # 100 requests per minute
        return False
else:
    request_counts[ip] = 1  # BUG: Should reset to 0, not 1
```

---

### BUG-013: Authorization Bypass in Update User
**Severity:** Critical  
**Category:** Security

**Description:**
Update user endpoint lacks authorization control. Users can update other users' information.

**Steps to Reproduce:**
1. Review API code (main.py lines 193-217)

**Expected Result:**
- Users should only be able to update their own information

**Actual Result:**
- No authorization control

**Evidence:**
```python
# Code in main.py lines 197-199
username = verify_session(authorization) if authorization else None
if not username:
    raise HTTPException(status_code=401, detail="Authentication required")
# BUG: No check if username matches the user being updated
```

---

### BUG-014: Information Disclosure in Stats Endpoint
**Severity:** Low  
**Category:** Security

**Description:**
Stats endpoint exposes session tokens and emails when called with include_details=true.

**Steps to Reproduce:**
1. Send a request to GET `/stats?include_details=true` endpoint

**Expected Result:**
- Sensitive information should not be exposed

**Actual Result:**
- Session tokens and emails are returned

**Evidence:**
```python
# Code in main.py lines 301-302
if include_details:
    stats["user_emails"] = [u["email"] for u in users_db.values()]
    stats["session_tokens"] = list(sessions.keys())[:5]  # BUG: Exposes tokens
```

---

### BUG-015: Bulk Create Endpoint Hidden
**Severity:** Medium  
**Category:** Security

**Description:**
Bulk create endpoint is hidden from schema but still accessible. This endpoint could allow rate limiting bypass.

**Steps to Reproduce:**
1. Review API code (main.py line 316)

**Expected Result:**
- Bulk endpoint should either be completely removed or made secure

**Actual Result:**
- Endpoint is hidden but accessible

**Evidence:**
```python
# Code in main.py line 316
@app.post("/users/bulk", include_in_schema=False)  # BUG: Hidden but accessible
```

---

### BUG-016: Rate Limiting Not Working Properly
**Severity:** Medium  
**Category:** Logic/Performance

**Description:**
Rate limiting tests are failing. Rate limiting mechanism is not working properly.

**Steps to Reproduce:**
1. Run `test_rate_limiting_performance` test

**Expected Result:**
- Rate limiting should work and some requests should return 429

**Actual Result:**
- Rate limiting is not working, all requests pass through

**Evidence:**
```
FAILED test_classes/test_performance.py::TestPerformance::test_rate_limiting_performance
assert rate_limited_count > 0
```

---

### BUG-017: Session Hijacking Vulnerability
**Severity:** High  
**Category:** Security

**Description:**
Predictable session tokens are accepted. Vulnerable to session hijacking attacks.

**Steps to Reproduce:**
1. Run `test_session_hijacking_attempt` test

**Expected Result:**
- Predictable tokens should be rejected (401)

**Actual Result:**
- Predictable tokens are accepted (200)

**Evidence:**
```
FAILED test_classes/test_security.py::TestSecurity::test_session_hijacking_attempt
assert response.status_code == 401
E   assert 200 == 401
```

---

### BUG-018: Rate Limiting Affecting Test Execution
**Severity:** Low  
**Category:** Performance

**Description:**
Rate limiting is affecting test execution. Tests are getting 429 Too Many Requests.

**Steps to Reproduce:**
1. Run the test suite

**Expected Result:**
- Tests should not be affected by rate limiting

**Actual Result:**
- Many tests are getting 429

**Evidence:**
```
FAILED test_classes/test_users.py::TestUserCRUD::test_create_user_valid
assert response.status_code == 201
E   assert 429 == 201
```

## Summary

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 5     | 28%        |
| High     | 4     | 22%        |
| Medium   | 6     | 33%        |
| Low      | 3     | 17%        |
| **Total**| **18**| **100%**   |

## Recommendations

1. **Immediate Actions (Critical Bugs):**
   - Replace MD5 hash with bcrypt
   - Replace static salt with unique salt
   - Enable session expiration
   - Fix authorization bypass
   - Fix login authentication

2. **High Priority (High Bugs):**
   - Fix username case sensitivity
   - Fix pagination logic
   - Fix search endpoint

3. **Medium Priority:**
   - Fix phone validation regex
   - Make username validation secure
   - Ensure user ID type consistency
   - Make bulk endpoint secure

4. **Low Priority:**
   - Fix rate limiting logic
   - Prevent information disclosure
