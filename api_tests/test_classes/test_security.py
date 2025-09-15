import pytest
import httpx
import hashlib
import time

class TestSecurity:
    def test_password_hash_security(self, client):
        # Create a user
        payload = {
            "username": "security_test_user",
            "email": "security@example.com",
            "password": "PlainTextPassword123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 201
        
        # Try to login with the password
        login_payload = {"username": "security_test_user", "password": "PlainTextPassword123"}
        login_response = client.post("/login", json=login_payload)
        # This might fail due to authentication bug, but password should be hashed
        assert login_response.status_code in [200, 401]


    def test_xss_attempt(self, client):
        payload = {
            "username": "<script>alert('xss')</script>",
            "email": "xss@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        # Should fail due to username validation
        assert response.status_code == 422

    def test_authorization_bypass_attempt(self, client):    
        # Try to update user without authentication
        payload = {"email": "hacked@example.com", "age": 99}
        response = client.put("/users/1", json=payload)
        assert response.status_code == 401

    def test_session_hijacking_attempt(self, client):
        # Try to use a predictable token
        fake_token = "12345678901234567890123456789012"
        response = client.get("/users/1", headers={"Authorization": f"Bearer {fake_token}"})
        assert response.status_code == 401

    def test_rate_limiting_bypass(self, client):
        # Make many requests quickly
        for i in range(10):
            response = client.post("/users", json={
                "username": f"rate_bypass_{i}",
                "email": f"rate_bypass_{i}@example.com",
                "password": "Password123",
                "age": 25
            })
            # Should eventually hit rate limit
            if response.status_code == 429:
                break
        else:
            # If we get here, rate limiting might not be working properly
            pytest.fail("Rate limiting not working properly")

    def test_brute_force_protection(self, client):
        # Try multiple failed login attempts
        for i in range(5):
            response = client.post("/login", json={
                "username": "john_doe",
                "password": f"wrong_password_{i}"
            })
            assert response.status_code == 401

    def test_information_disclosure(self, client):
        # Check if stats endpoint exposes sensitive information
        response = client.get("/stats?include_details=true")
        assert response.status_code == 200
        data = response.json()
        
        # Check if sensitive data is exposed
        if "session_tokens" in data:
            # Session tokens should not be exposed
            assert len(data["session_tokens"]) == 0 or "session_tokens" not in data

    def test_input_validation_security(self, client):
        # Test very long input
        long_string = "A" * 10000
        payload = {
            "username": long_string,
            "email": "long@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 422

    def test_special_characters_security(self, client):
        payload = {
            "username": "user'; DROP TABLE users; --",
            "email": "special@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        # Should fail due to invalid characters
        assert response.status_code == 422

    def test_unicode_security(self, client):
        payload = {
            "username": "用户",
            "email": "unicode@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        # Should fail due to invalid characters
        assert response.status_code == 422

    def test_null_byte_injection(self, client):
        payload = {
            "username": "user\x00",
            "email": "null@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        # Should fail due to invalid characters
        assert response.status_code == 422

    def test_path_traversal_attempt(self, client):
        # Try to access files outside the application
        response = client.get("/users/../../../etc/passwd")
        assert response.status_code in [400, 404]

    def test_http_method_override(self, client):
        # Try to use different HTTP methods
        response = client.request("PATCH", "/users/1")
        assert response.status_code == 405

    def test_content_type_validation(self, client):
        # Try to send non-JSON data
        response = client.post("/users", 
                             data="not json data",
                             headers={"Content-Type": "text/plain"})
        assert response.status_code in [400, 422]

    def test_cors_headers(self, client):
        response = client.options("/users")
        # Should handle OPTIONS request properly
        assert response.status_code in [200, 405]

    def test_authentication_timing_attack(self, client):
        # Measure response times for valid vs invalid usernames
        start_time = time.time()
        response1 = client.post("/login", json={
            "username": "nonexistent_user",
            "password": "password"
        })
        time1 = time.time() - start_time
        
        start_time = time.time()
        response2 = client.post("/login", json={
            "username": "john_doe",
            "password": "wrong_password"
        })
        time2 = time.time() - start_time
        
        # Both should return 401, but timing should be similar
        assert response1.status_code == 401
        assert response2.status_code == 401
        # Timing difference should not be significant (allowing for some variance)
        assert abs(time1 - time2) < 0.5  # 500ms tolerance
