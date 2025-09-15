# Bug Report - User Management API

## Executive Summary

Bu rapor, User Management API'sinde tespit edilen bugları detaylandırmaktadır. Toplam **18 adet bug** tespit edilmiş olup, bunların **5'i Critical**, **4'ü High**, **6'sı Medium** ve **3'ü Low** seviyesindedir.

**Test Sonuçları:** 74 test çalıştırıldı, 56 başarılı, 18 başarısız, 1 uyarı

## Bug Listesi

### BUG-001: Login Endpoint Authentication Failure
**Severity:** Critical  
**Category:** Authentication/Security

**Description:**
Login endpoint'i geçerli kullanıcı bilgileriyle bile 401 Unauthorized döndürüyor. Test verilerinde bulunan `john_doe` kullanıcısı ile giriş yapılamıyor.

**Steps to Reproduce:**
1. API'yi başlatın
2. Test verilerini yükleyin (`python seed_data.py`)
3. POST `/login` endpoint'ine şu payload ile istek gönderin:
```json
{
    "username": "john_doe",
    "password": "password123"
}
```

**Expected Result:**
- Status Code: 200
- Response: Token ve kullanıcı bilgileri

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
Aynı username'in farklı case'lerde (büyük/küçük harf) birden fazla kez oluşturulabilmesi. Username'ler case-insensitive olarak saklanıyor ama duplicate kontrolü case-sensitive yapılıyor.

**Steps to Reproduce:**
1. `CaseSensitiveUser` username'i ile kullanıcı oluşturun
2. `casesensitiveuser` username'i ile aynı kullanıcıyı tekrar oluşturmaya çalışın

**Expected Result:**
- İkinci istek 400 Bad Request döndürmeli
- "Username already exists" hatası

**Actual Result:**
- İkinci istek 201 Created döndürüyor
- Kullanıcı başarıyla oluşturuluyor

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
Pagination'da limit+1 kadar kayıt döndürülüyor. Limit 5 olarak ayarlandığında 6 kayıt döndürülüyor.

**Steps to Reproduce:**
1. GET `/users?limit=5&offset=0` endpoint'ine istek gönderin

**Expected Result:**
- Maksimum 5 kayıt döndürülmeli

**Actual Result:**
- 6 kayıt döndürülüyor

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
Search endpoint'i geçerli query parametreleriyle bile 400 Bad Request döndürüyor. Tüm search testleri başarısız oluyor.

**Steps to Reproduce:**
1. GET `/users/search?q=john` endpoint'ine istek gönderin

**Expected Result:**
- Status Code: 200
- Kullanıcı listesi

**Actual Result:**
- Status Code: 400
- Bad Request hatası

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
Logout endpoint'i geçersiz token ile çağrıldığında "Logged out successfully" mesajı döndürüyor. Geçersiz token'lar için "No active session" döndürmeli.

**Steps to Reproduce:**
1. POST `/logout` endpoint'ine geçersiz token ile istek gönderin:
```
Authorization: Bearer invalid_token
```

**Expected Result:**
- "No active session" mesajı

**Actual Result:**
- "Logged out successfully" mesajı

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
Şifreler MD5 ile hash'leniyor. MD5 güvenli değil ve rainbow table saldırılarına açık.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py line 68-69)

**Expected Result:**
- bcrypt, scrypt veya Argon2 gibi güvenli hash algoritması kullanılmalı

**Actual Result:**
- MD5 kullanılıyor

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
Tüm şifreler için aynı static salt kullanılıyor. Bu güvenlik açığı oluşturuyor.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py line 68)

**Expected Result:**
- Her şifre için unique salt kullanılmalı

**Actual Result:**
- Tüm şifreler için "static_salt_2024" kullanılıyor

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
Session expiration kontrolü yorum satırına alınmış. Session'lar hiç expire olmuyor.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py lines 130-131)

**Expected Result:**
- Session'lar belirli süre sonra expire olmalı

**Actual Result:**
- Session'lar hiç expire olmuyor

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
Telefon numarası validation regex'i yanlış. Geçerli telefon numaralarını reddediyor.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py line 40)

**Expected Result:**
- Geçerli telefon numaraları kabul edilmeli

**Actual Result:**
- Regex yanlış, geçerli numaralar reddediliyor

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
Username validation'da tehlikeli karakterlere izin veriliyor (', ", ;).

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py line 34)

**Expected Result:**
- Sadece güvenli karakterlere izin verilmeli

**Actual Result:**
- Tehlikeli karakterlere izin veriliyor

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
User ID bazen string bazen integer olarak işleniyor. get_user endpoint'inde string kabul ediliyor ama diğer endpoint'lerde integer bekleniyor.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py lines 179-186 vs 193-196)

**Expected Result:**
- Tüm endpoint'lerde tutarlı type kullanılmalı

**Actual Result:**
- Type inconsistency var

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
Rate limiting'de time window hesaplaması yanlış. 60 saniye sonra counter reset olmuyor.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py lines 72-88)

**Expected Result:**
- 60 saniye sonra counter reset olmalı

**Actual Result:**
- Counter reset logic'i hatalı

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
Update user endpoint'inde authorization kontrolü eksik. Kullanıcılar başka kullanıcıların bilgilerini güncelleyebiliyor.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py lines 193-217)

**Expected Result:**
- Kullanıcılar sadece kendi bilgilerini güncelleyebilmeli

**Actual Result:**
- Authorization kontrolü yok

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
Stats endpoint'i include_details=true ile çağrıldığında session token'ları ve email'leri expose ediyor.

**Steps to Reproduce:**
1. GET `/stats?include_details=true` endpoint'ine istek gönderin

**Expected Result:**
- Hassas bilgiler expose edilmemeli

**Actual Result:**
- Session token'ları ve email'ler döndürülüyor

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
Bulk create endpoint'i schema'dan gizlenmiş ama hala erişilebilir. Bu endpoint rate limiting bypass'ına izin verebilir.

**Steps to Reproduce:**
1. API kodunu inceleyin (main.py line 316)

**Expected Result:**
- Bulk endpoint ya tamamen kaldırılmalı ya da güvenli hale getirilmeli

**Actual Result:**
- Endpoint gizli ama erişilebilir

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
Rate limiting test'leri başarısız oluyor. Rate limiting mekanizması düzgün çalışmıyor.

**Steps to Reproduce:**
1. `test_rate_limiting_performance` test'ini çalıştırın

**Expected Result:**
- Rate limiting çalışmalı ve bazı istekler 429 döndürmeli

**Actual Result:**
- Rate limiting çalışmıyor, tüm istekler geçiyor

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
Predictable session token'lar kabul ediliyor. Session hijacking saldırılarına açık.

**Steps to Reproduce:**
1. `test_session_hijacking_attempt` test'ini çalıştırın

**Expected Result:**
- Predictable token'lar reddedilmeli (401)

**Actual Result:**
- Predictable token'lar kabul ediliyor (200)

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
Rate limiting test execution'ı etkiliyor. Test'ler 429 Too Many Requests alıyor.

**Steps to Reproduce:**
1. Test suite'ini çalıştırın

**Expected Result:**
- Test'ler rate limiting'den etkilenmemeli

**Actual Result:**
- Birçok test 429 alıyor

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
   - MD5 hash'i bcrypt ile değiştir
   - Static salt'ı unique salt ile değiştir
   - Session expiration'ı aktif et
   - Authorization bypass'ı düzelt
   - Login authentication'ı düzelt

2. **High Priority (High Bugs):**
   - Username case sensitivity'yi düzelt
   - Pagination logic'ini düzelt
   - Search endpoint'ini düzelt

3. **Medium Priority:**
   - Phone validation regex'ini düzelt
   - Username validation'ı güvenli hale getir
   - User ID type consistency'yi sağla
   - Bulk endpoint'i güvenli hale getir

4. **Low Priority:**
   - Rate limiting logic'ini düzelt
   - Information disclosure'ı engelle
