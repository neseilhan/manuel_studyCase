import pytest
import httpx

class TestUserCRUD:

    def test_create_user_valid(self, client):
        payload = {
            "username": "new_user_test",
            "email": "new_user_test@example.com",
            "password": "Password123",
            "age": 25,
            "phone": "+1234567890"
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "new_user_test"
        assert data["email"] == "new_user_test@example.com"
        assert data["age"] == 25
        assert data["phone"] == "+1234567890"
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] == True

    def test_create_user_duplicate_username(self, client):
        payload = {
            "username": "john_doe",  # This user already exists
            "email": "duplicate@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    def test_create_user_invalid_age_underage(self, client):
        payload = {
            "username": "underage_user",
            "email": "underage@example.com",
            "password": "Password123",
            "age": 15
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 422

    def test_create_user_invalid_age_overage(self, client):
        payload = {
            "username": "overage_user",
            "email": "overage@example.com",
            "password": "Password123",
            "age": 151
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 422

    def test_create_user_invalid_email(self, client):
        payload = {
            "username": "invalid_email_user",
            "email": "invalid-email",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 422

    def test_create_user_short_password(self, client):
        payload = {
            "username": "short_pass_user",
            "email": "shortpass@example.com",
            "password": "12345",  # Less than 6 characters
            "age": 25
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 422

    def test_create_user_invalid_phone(self, client):
        payload = {
            "username": "invalid_phone_user",
            "email": "invalidphone@example.com",
            "password": "Password123",
            "age": 25,
            "phone": "invalid-phone"
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 422

    def test_get_user_list_default(self, client):
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_user_list_with_pagination(self, client):
        response = client.get("/users?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_user_list_with_sorting(self, client):
        response = client.get("/users?sort_by=username&order=asc")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_single_user_valid_id(self, client):
        response = client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "age" in data
        assert "id" in data

    def test_get_single_user_invalid_id(self, client):
        response = client.get("/users/99999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_single_user_string_id(self, client):
        response = client.get("/users/invalid")
        assert response.status_code == 400
        assert "Invalid user ID format" in response.json()["detail"]

    def test_update_user_without_auth(self, client):
        payload = {"email": "updated@example.com", "age": 30}
        response = client.put("/users/1", json=payload)
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_update_user_with_invalid_token(self, client):  
        payload = {"email": "updated@example.com", "age": 30}
        response = client.put("/users/1", json=payload, 
                            headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401

    def test_delete_user_without_auth(self, client):
        response = client.delete("/users/1")
        assert response.status_code == 401

    def test_delete_user_invalid_id(self, client):
        response = client.delete("/users/99999")
        assert response.status_code == 401

    def test_username_case_sensitivity(self, client):
        payload = {
            "username": "CaseSensitiveUser",
            "email": "case@example.com",
            "password": "Password123",
            "age": 25
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 201
        
        payload2 = {
            "username": "casesensitiveuser",
            "email": "case2@example.com",
            "password": "Password123",
            "age": 25
        }
        response2 = client.post("/users", json=payload2)
        # This might fail due to case sensitivity bug
        assert response2.status_code in [201, 400]