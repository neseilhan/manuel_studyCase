# Test Documentation - User Management API

## Overview

This documentation explains how to run the test suite written for the User Management API. The test suite is written using the pytest framework and contains 76 test cases.

## Prerequisites

### Required Software:
- Python 3.10+
- pip (Python package manager)

### Required Python Packages:
- pytest
- httpx
- pytest-asyncio
- jsonschema

## Installation

### 1. Install Main Dependencies
```bash
# In the main project directory
pip install -r requirements.txt
```

### 2. Install Test Dependencies
```bash
# In the test directory
cd api_tests
pip install -r requirements_test.txt
```

## Setup Instructions

### 1. Start the API Server
```bash
# In the main project directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

After starting the API server, it will be accessible at these URLs:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 2. Seed Test Data
```bash
# In the main project directory (new terminal)
python seed_data.py
```

This command creates the necessary user data for testing:
- Username: `john_doe`, Password: `password123`
- Username: `jane_smith`, Password: `securepass456`
- Username: `admin_user`, Password: `Admin@2024`
- And other test users...

## Running Tests

### 1. Run All Tests
```bash
# In the api_tests directory
cd api_tests
python -m pytest test_classes/ -v
```

### 2. Run Specific Test Files
```bash
# Authentication tests
python -m pytest test_classes/test_auth.py -v

# User CRUD tests
python -m pytest test_classes/test_users.py -v

# Miscellaneous tests
python -m pytest test_classes/test_other.py -v

# Security tests
python -m pytest test_classes/test_security.py -v

# Performance tests
python -m pytest test_classes/test_performance.py -v
```

### 3. Run Specific Test Classes
```bash
# TestAuth class only
python -m pytest test_classes/test_auth.py::TestAuth -v

# TestUserCRUD class only
python -m pytest test_classes/test_users.py::TestUserCRUD -v

# TestMisc class only
python -m pytest test_classes/test_other.py::TestMisc -v

# TestSecurity class only
python -m pytest test_classes/test_security.py::TestSecurity -v

# TestPerformance class only
python -m pytest test_classes/test_performance.py::TestPerformance -v
```

### 4. Run Specific Test Methods
```bash
# Single test method
python -m pytest test_classes/test_auth.py::TestAuth::test_login_valid -v
```

### 5. Run Tests with Coverage
```bash
# Install coverage if not already installed
pip install pytest-cov

# Run tests with coverage
python -m pytest test_classes/ --cov=../main --cov-report=html -v
```

### 6. Run Tests in Parallel
```bash
# Install pytest-xdist if not already installed
pip install pytest-xdist

# Run tests in parallel
python -m pytest test_classes/ -n auto -v
```

## Test Output Examples

### Successful Test Run (Expected):
```
========================================= test session starts ==========================================
platform win32 -- Python 3.13.7, pytest-8.4.2
collected 76 items

test_classes/test_auth.py::TestAuth::test_login_invalid_username PASSED    [  2%]
test_classes/test_auth.py::TestAuth::test_login_invalid_password PASSED    [  4%]
test_classes/test_users.py::TestUserCRUD::test_create_user_invalid_age_underage PASSED [  6%]
...
========================================= 76 passed in 13.56s ==========================================
```

### Failed Test Run (Current Status):
```
========================================= test session starts ==========================================
collected 76 items

test_classes/test_auth.py::TestAuth::test_logout_invalid_token FAILED      [  1%]
test_classes/test_auth.py::TestAuth::test_token_expiration_handling FAILED  [  2%]
test_classes/test_other.py::TestMisc::test_health_check_memory_counts FAILED [  3%]
test_classes/test_other.py::TestMisc::test_search_users_by_username FAILED  [  4%]
test_classes/test_other.py::TestMisc::test_search_users_by_email FAILED     [  5%]
test_classes/test_other.py::TestMisc::test_search_users_field_username FAILED [  6%]
test_classes/test_other.py::TestMisc::test_search_users_field_email FAILED   [  7%]
test_classes/test_other.py::TestMisc::test_search_users_exact_match FAILED   [  8%]
test_classes/test_other.py::TestMisc::test_search_users_empty_query FAILED   [  9%]
test_classes/test_other.py::TestMisc::test_search_users_invalid_field FAILED [ 10%]
test_classes/test_performance.py::TestPerformance::test_rate_limiting_performance FAILED [ 11%]
test_classes/test_security.py::TestSecurity::test_password_hash_security FAILED [ 12%]
test_classes/test_security.py::TestSecurity::test_session_hijacking_attempt FAILED [ 13%]
test_classes/test_security.py::TestSecurity::test_information_disclosure FAILED [ 14%]
test_classes/test_users.py::TestUserCRUD::test_create_user_valid FAILED      [ 15%]
test_classes/test_users.py::TestUserCRUD::test_get_user_list_with_pagination FAILED [ 16%]
test_classes/test_users.py::TestUserCRUD::test_username_case_sensitivity FAILED [ 17%]
...
========================================= 17 failed, 59 passed, 1 warning in 13.56s ======================================
```

## Test Structure

### Test Files:
- `test_auth.py` - Authentication and session management tests (8 tests)
- `test_users.py` - User CRUD operations tests (15 tests)
- `test_other.py` - Other endpoints and miscellaneous tests (21 tests)
- `test_security.py` - Security tests (3 tests)
- `test_performance.py` - Performance tests (1 test)

### Test Classes:
- `TestAuth` - Login, logout, session management (8 tests)
- `TestUserCRUD` - Create, read, update, delete operations (15 tests)
- `TestMisc` - Search, stats, health check, edge cases (21 tests)
- `TestSecurity` - Security vulnerability tests (3 tests)
- `TestPerformance` - Performance and load tests (1 test)

### Test Categories:
- **Positive Tests** - Expected results with valid inputs
- **Negative Tests** - Error conditions with invalid inputs
- **Edge Cases** - Boundary conditions and limit values
- **Security Tests** - Authentication, authorization, input validation, XSS, SQL injection
- **Performance Tests** - Rate limiting, concurrent requests, response time
- **Bug Detection Tests** - Tests that detect known bugs in the API

## Troubleshooting

### Common Issues:

#### 1. API Server Not Running
**Error:** `ConnectionError: [Errno 111] Connection refused`
**Solution:** 
```bash
# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Test Data Not Available
**Error:** `401 Unauthorized` for valid credentials
**Solution:**
```bash
# Load test data
python seed_data.py
```

#### 3. Port Already in Use
**Error:** `[Errno 98] Address already in use`
**Solution:**
```bash
# Use a different port
uvicorn main:app --reload --host 0.0.0.0 --port 8001
# Update BASE_URL in conftest.py
```

#### 4. Import Errors
**Error:** `ModuleNotFoundError: No module named 'httpx'`
**Solution:**
```bash
# Install test dependencies
pip install -r requirements_test.txt
```

#### 5. Test Isolation Issues
**Error:** Tests failing due to shared state
**Solution:**
```bash
# Restart API before each test
# Or clean test data before each test
```

## Test Configuration

### conftest.py
```python
import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL)
```

### pytest.ini (Optional)
```ini
[tool:pytest]
testpaths = test_classes
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## Continuous Integration

### GitHub Actions

#### How to View Test Results:

1. **Go to GitHub Repository**
   - Navigate to your repository on GitHub
   - Click on the "Actions" tab

2. **View Workflow Runs**
   - You'll see a list of workflow runs
   - Click on the latest run to see details

3. **Check Test Results**
   - In the workflow run page, you'll see:
     - ✅ **Green checkmark** = All tests passed
     - ❌ **Red X** = Some tests failed
     - ⚠️ **Yellow warning** = Tests passed with warnings

4. **Download Test Reports**
   - Scroll down to "Artifacts" section
   - Download `test-reports-{run-number}` artifact
   - Extract and open `test-report.html` for detailed results

5. **View Test Summary**
   - In the workflow run page, scroll down to see:
     - Test execution summary
     - Pass/fail statistics
     - Failed test details
     - Performance metrics
 
## Test Reports

### HTML Report:
```bash
# Install pytest-html
pip install pytest-html

# Generate HTML report
python -m pytest test_classes/ --html=report.html --self-contained-html
```

### JUnit XML Report:
```bash
# Generate JUnit XML report
python -m pytest test_classes/ --junitxml=report.xml
```

### Coverage Report:
```bash
# Generate coverage report
python -m pytest test_classes/ --cov=../main --cov-report=html --cov-report=term
```

## Best Practices

1. **Test Isolation** - Each test should be independent
2. **Clear Test Names** - Test names should explain what they test
3. **Assertion Messages** - Error messages should be descriptive
4. **Test Data Management** - Test data should be manageable
5. **Error Handling** - Tests should handle expected errors
6. **Performance Considerations** - Tests should run fast
7. **Documentation** - Tests should be documented

## Contact

For questions about the test suite:
- Review the test files
- Check the bug report
- Read the test report
