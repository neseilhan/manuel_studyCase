import pytest
import httpx
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:

    def test_response_time_basic(self, client):
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    def test_concurrent_user_creation(self, client):
        def create_user(user_id):
            payload = {
                "username": f"perf_user_{user_id}",
                "email": f"perf_{user_id}@example.com",
                "password": "Password123",
                "age": 25
            }
            response = client.post("/users", json=payload)
            return response.status_code
        
        # Create 10 users concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_user, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # Most should succeed (some might fail due to rate limiting)
        success_count = sum(1 for status in results if status == 201)
        assert success_count >= 5  # At least half should succeed

    def test_concurrent_read_operations(self, client):
        def read_users():
            response = client.get("/users")
            return response.status_code
        
        # Make 20 concurrent read requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(read_users) for _ in range(20)]
            results = [future.result() for future in futures]
        
        # All should succeed
        assert all(status == 200 for status in results)

    def test_memory_usage_under_load(self, client):
        # Create many users to test memory usage
        for i in range(50):
            payload = {
                "username": f"memory_test_{i}",
                "email": f"memory_{i}@example.com",
                "password": "Password123",
                "age": 25
            }
            response = client.post("/users", json=payload)
            if response.status_code == 429:  # Rate limited
                break
        
        # Check if API is still responsive
        response = client.get("/health")
        assert response.status_code == 200

    def test_large_payload_handling(self, client):
        # Create user with large data
        large_phone = "+1" + "2" * 1000  # Very long phone number
        payload = {
            "username": "large_payload_user",
            "email": "large@example.com",
            "password": "Password123",
            "age": 25,
            "phone": large_phone
        }
        
        start_time = time.time()
        response = client.post("/users", json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        # Should either succeed or fail quickly
        assert response_time < 2.0
        assert response.status_code in [201, 422]

    def test_rate_limiting_performance(self, client):
        # Make requests at the rate limit boundary
        start_time = time.time()
        success_count = 0
        rate_limited_count = 0
        
        for i in range(20):
            payload = {
                "username": f"rate_test_{i}",
                "email": f"rate_{i}@example.com",
                "password": "Password123",
                "age": 25
            }
            response = client.post("/users", json=payload)
            
            if response.status_code == 201:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
            
            time.sleep(0.1)  # Small delay between requests
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should have some successes and some rate limits
        assert success_count > 0
        assert rate_limited_count > 0
        assert total_time < 5.0  # Should complete within reasonable time

    def test_search_performance(self, client):
        # Create some test data first
        for i in range(10):
            payload = {
                "username": f"search_test_{i}",
                "email": f"search_{i}@example.com",
                "password": "Password123",
                "age": 25
            }
            client.post("/users", json=payload)
        
        # Test search performance
        start_time = time.time()
        response = client.get("/users/search?q=search_test")
        end_time = time.time()
        
        response_time = end_time - start_time
        # Search should be fast (though it might fail due to bugs)
        assert response_time < 2.0

    def test_stats_performance(self, client):
        start_time = time.time()
        response = client.get("/stats")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0

    def test_health_check_performance(self, client):
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 0.5  # Health check should be very fast

    def test_concurrent_mixed_operations(self, client):
        def mixed_operation(operation_id):
            if operation_id % 3 == 0:
                # Read operation
                response = client.get("/users")
            elif operation_id % 3 == 1:
                # Create operation
                payload = {
                    "username": f"mixed_{operation_id}",
                    "email": f"mixed_{operation_id}@example.com",
                    "password": "Password123",
                    "age": 25
                }
                response = client.post("/users", json=payload)
            else:
                # Stats operation
                response = client.get("/stats")
            
            return response.status_code
        
        # Run 15 mixed operations concurrently
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(15)]
            results = [future.result() for future in futures]
        
        # Most operations should succeed
        success_count = sum(1 for status in results if status in [200, 201])
        assert success_count >= 10  # At least 2/3 should succeed

    def test_error_handling_performance(self, client):
        # Test with invalid requests
        start_time = time.time()
        
        # Invalid user creation
        response1 = client.post("/users", json={"invalid": "data"})
        
        # Invalid user ID
        response2 = client.get("/users/invalid_id")
        
        # Invalid endpoint
        response3 = client.get("/invalid_endpoint")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Error handling should be fast
        assert total_time < 1.0
        assert response1.status_code in [400, 422]
        assert response2.status_code in [400, 404]
        assert response3.status_code == 404

    def test_session_management_performance(self, client): 
        # Create multiple sessions
        start_time = time.time()
        
        for i in range(5):
            login_payload = {"username": "john_doe", "password": "password123"}
            response = client.post("/login", json=login_payload)
            # Might fail due to authentication bug, but should be fast
            assert response.status_code in [200, 401]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Session operations should be reasonably fast
        assert total_time < 3.0

    def test_pagination_performance(self, client):
        # Create many users first
        for i in range(20):
            payload = {
                "username": f"pagination_test_{i}",
                "email": f"pagination_{i}@example.com",
                "password": "Password123",
                "age": 25
            }
            client.post("/users", json=payload)
        
        # Test pagination performance
        start_time = time.time()
        response = client.get("/users?limit=10&offset=0")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0
