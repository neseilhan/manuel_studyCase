# Test Documentation - User Management API

## Overview

Bu dokümantasyon, User Management API'si için yazılan test suite'inin nasıl çalıştırılacağını açıklar. Test suite pytest framework'ü kullanılarak yazılmıştır ve 74 test case içerir.

**Güncel Test Durumu:**
- ✅ 56 test başarılı (%75.7)
- ❌ 18 test başarısız (%24.3)
- ⚠️ 1 uyarı
- 🐛 18 bug tespit edildi

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
# Ana proje dizininde
pip install -r requirements.txt
```

### 2. Install Test Dependencies
```bash
# Test dizininde
cd api_tests
pip install -r requirements_test.txt
```

## Setup Instructions

### 1. Start the API Server
```bash
# Ana proje dizininde
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API server'ı başlattıktan sonra şu URL'lerde erişilebilir:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 2. Seed Test Data
```bash
# Ana proje dizininde (yeni terminal)
python seed_data.py
```

Bu komut test için gerekli kullanıcı verilerini oluşturur:
- Username: `john_doe`, Password: `password123`
- Username: `jane_smith`, Password: `securepass456`
- Username: `admin_user`, Password: `Admin@2024`
- Ve diğer test kullanıcıları...

## Running Tests

### 1. Run All Tests
```bash
# api_tests dizininde
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
```

### 3. Run Specific Test Classes
```bash
# TestAuth class only
python -m pytest test_classes/test_auth.py::TestAuth -v

# TestUserCRUD class only
python -m pytest test_classes/test_users.py::TestUserCRUD -v

# TestMisc class only
python -m pytest test_classes/test_other.py::TestMisc -v
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

### Successful Test Run:
```
========================================= test session starts ==========================================
platform win32 -- Python 3.13.7, pytest-8.4.2
collected 74 items

test_classes/test_auth.py::TestAuth::test_login_invalid_username PASSED    [  2%]
test_classes/test_auth.py::TestAuth::test_login_invalid_password PASSED    [  4%]
test_classes/test_users.py::TestUserCRUD::test_create_user_invalid_age_underage PASSED [  6%]
...
========================================= 74 passed in 12.42s ==========================================
```

### Failed Test Run (Güncel Durum):
```
========================================= test session starts ==========================================
collected 74 items

test_classes/test_auth.py::TestAuth::test_login_valid FAILED              [  1%]
test_classes/test_users.py::TestUserCRUD::test_create_user_valid FAILED    [  2%]
...
========================================= 18 failed, 56 passed, 1 warning in 12.42s ======================================
```

## Test Structure

### Test Files:
- `test_auth.py` - Authentication ve session management testleri (8 test)
- `test_users.py` - User CRUD operations testleri (15 test)
- `test_other.py` - Diğer endpoint'ler ve miscellaneous testler (21 test)
- `test_security.py` - Security testleri (15 test)
- `test_performance.py` - Performance testleri (15 test)

### Test Classes:
- `TestAuth` - Login, logout, session management (8 test)
- `TestUserCRUD` - Create, read, update, delete operations (15 test)
- `TestMisc` - Search, stats, health check, edge cases (21 test)
- `TestSecurity` - Security vulnerability tests (15 test)
- `TestPerformance` - Performance ve load tests (15 test)

### Test Categories:
- **Positive Tests** - Geçerli input'larla beklenen sonuçlar
- **Negative Tests** - Geçersiz input'larla hata durumları
- **Edge Cases** - Boundary conditions ve limit değerler
- **Security Tests** - Authentication, authorization, input validation, XSS, SQL injection
- **Performance Tests** - Rate limiting, concurrent requests, response time
- **Bug Detection Tests** - API'deki bilinen bug'ları tespit eden testler

## Troubleshooting

### Common Issues:

#### 1. API Server Not Running
**Error:** `ConnectionError: [Errno 111] Connection refused`
**Solution:** 
```bash
# API server'ı başlatın
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Test Data Not Available
**Error:** `401 Unauthorized` for valid credentials
**Solution:**
```bash
# Test verilerini yükleyin
python seed_data.py
```

#### 3. Port Already in Use
**Error:** `[Errno 98] Address already in use`
**Solution:**
```bash
# Farklı port kullanın
uvicorn main:app --reload --host 0.0.0.0 --port 8001
# conftest.py'de BASE_URL'i güncelleyin
```

#### 4. Import Errors
**Error:** `ModuleNotFoundError: No module named 'httpx'`
**Solution:**
```bash
# Test dependencies'leri yükleyin
pip install -r requirements_test.txt
```

#### 5. Test Isolation Issues
**Error:** Tests failing due to shared state
**Solution:**
```bash
# Her test öncesi API'yi restart edin
# Veya test data'yı her test öncesi temizleyin
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

### GitHub Actions Example:
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r api_tests/requirements_test.txt
    - name: Start API server
      run: |
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        sleep 5
    - name: Seed test data
      run: python seed_data.py
    - name: Run tests
      run: |
        cd api_tests
        python -m pytest test_classes/ -v
```

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

1. **Test Isolation** - Her test bağımsız olmalı
2. **Clear Test Names** - Test isimleri ne test ettiğini açıklamalı
3. **Assertion Messages** - Hata mesajları açıklayıcı olmalı
4. **Test Data Management** - Test verileri yönetilebilir olmalı
5. **Error Handling** - Test'ler beklenen hataları handle etmeli
6. **Performance Considerations** - Test'ler hızlı çalışmalı
7. **Documentation** - Test'ler dokümante edilmeli

## Contact

Test suite ile ilgili sorularınız için:
- Test dosyalarını inceleyin
- Bug report'u kontrol edin
- Test report'u okuyun
