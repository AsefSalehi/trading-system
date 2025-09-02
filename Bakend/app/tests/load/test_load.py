"""
Load testing script using Locust for the Trading Backend API

This script tests the performance of cryptocurrency listing endpoints
under various load conditions.
"""

import random
from locust import HttpUser, task, between
from locust.exception import RescheduleTask


class CryptocurrencyAPIUser(HttpUser):
    """
    User behavior for testing cryptocurrency API endpoints
    """
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        self.client.verify = False  # Disable SSL verification for testing
        
        # Test data
        self.crypto_symbols = ["BTC", "ETH", "ADA", "DOT", "LINK", "UNI", "AAVE"]
        self.valid_sort_fields = ["market_cap", "market_cap_rank", "total_volume", "current_price"]
        self.valid_orders = ["asc", "desc"]
        self.valid_categories = ["market_cap", "volume", "gainers", "losers"]
    
    @task(10)
    def list_cryptocurrencies_default(self):
        """Test default cryptocurrency listing (most common operation)"""
        with self.client.get("/api/v1/cryptocurrencies/", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "items" in data and isinstance(data["items"], list):
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(5)
    def list_cryptocurrencies_with_pagination(self):
        """Test cryptocurrency listing with pagination"""
        skip = random.randint(0, 100)
        limit = random.choice([10, 25, 50, 100])
        
        params = {
            "skip": skip,
            "limit": limit
        }
        
        with self.client.get("/api/v1/cryptocurrencies/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data["items"]) <= limit:
                    response.success()
                else:
                    response.failure("Returned more items than limit")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def list_cryptocurrencies_with_sorting(self):
        """Test cryptocurrency listing with different sorting options"""
        sort_by = random.choice(self.valid_sort_fields)
        order = random.choice(self.valid_orders)
        
        params = {
            "sort_by": sort_by,
            "order": order,
            "limit": 20
        }
        
        with self.client.get("/api/v1/cryptocurrencies/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def list_cryptocurrencies_with_filters(self):
        """Test cryptocurrency listing with market filters"""
        params = {}
        
        # Add random filters
        if random.choice([True, False]):
            params["symbol_filter"] = random.choice(["BT", "ET", "A", "D"])
        
        if random.choice([True, False]):
            params["min_market_cap"] = random.choice([1000000, 10000000, 100000000])
        
        if random.choice([True, False]):
            params["min_volume"] = random.choice([1000000, 10000000, 50000000])
        
        params["limit"] = 50
        
        with self.client.get("/api/v1/cryptocurrencies/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(4)
    def get_cryptocurrency_by_symbol(self):
        """Test getting individual cryptocurrency data"""
        symbol = random.choice(self.crypto_symbols)
        
        with self.client.get(f"/api/v1/cryptocurrencies/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("symbol") == symbol:
                    response.success()
                else:
                    response.failure("Symbol mismatch in response")
            elif response.status_code == 404:
                # 404 is acceptable for non-existent cryptocurrencies
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def get_price_history(self):
        """Test getting price history data"""
        symbol = random.choice(self.crypto_symbols)
        limit = random.choice([10, 50, 100])
        
        params = {"limit": limit}
        
        with self.client.get(f"/api/v1/cryptocurrencies/{symbol}/history", params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("symbol") == symbol and "items" in data:
                    response.success()
                else:
                    response.failure("Invalid price history response format")
            elif response.status_code == 404:
                # 404 is acceptable for non-existent cryptocurrencies
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_top_cryptocurrencies(self):
        """Test getting top cryptocurrencies by category"""
        category = random.choice(self.valid_categories)
        limit = random.choice([5, 10, 20])
        
        params = {"limit": limit}
        
        with self.client.get(f"/api/v1/cryptocurrencies/top/{category}", params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) <= limit:
                    response.success()
                else:
                    response.failure("Invalid top cryptocurrencies response")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def check_health_endpoint(self):
        """Test health check endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check failed")
            else:
                response.failure(f"Health check returned {response.status_code}")
    
    # Less frequent tasks
    @task(0.5)
    def sync_cryptocurrency_data(self):
        """Test data synchronization endpoint (less frequent)"""
        params = {
            "limit": random.choice([10, 50]),
            "provider": random.choice(["coingecko", "coinmarketcap"])
        }
        
        with self.client.post("/api/v1/cryptocurrencies/sync", params=params, catch_response=True) as response:
            if response.status_code in [200, 429]:  # 429 for rate limiting is acceptable
                response.success()
            else:
                response.failure(f"Sync returned {response.status_code}")


class HeavyLoadUser(HttpUser):
    """
    User simulation for heavy load testing
    """
    
    wait_time = between(0.1, 1)  # Much faster requests
    
    @task
    def rapid_list_requests(self):
        """Rapid fire requests to test system under heavy load"""
        with self.client.get("/api/v1/cryptocurrencies/?limit=10", catch_response=True) as response:
            if response.status_code in [200, 429]:  # Accept rate limiting
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class ReadOnlyUser(HttpUser):
    """
    User that only performs read operations (most realistic for API)
    """
    
    wait_time = between(2, 8)
    
    @task(15)
    def browse_cryptocurrencies(self):
        """Simulate user browsing cryptocurrency listings"""
        # Start with first page
        self.client.get("/api/v1/cryptocurrencies/?limit=20")
        
        # Browse a few more pages
        for page in range(1, 4):
            skip = page * 20
            self.client.get(f"/api/v1/cryptocurrencies/?limit=20&skip={skip}")
    
    @task(8)
    def view_specific_cryptos(self):
        """Simulate user viewing specific cryptocurrencies"""
        symbols = ["BTC", "ETH", "ADA"]
        for symbol in symbols:
            self.client.get(f"/api/v1/cryptocurrencies/{symbol}")
    
    @task(3)
    def check_price_history(self):
        """Simulate user checking price history"""
        symbol = random.choice(["BTC", "ETH"])
        self.client.get(f"/api/v1/cryptocurrencies/{symbol}/history?limit=30")


# Custom load test scenarios
class SpikeLoadUser(HttpUser):
    """
    User for spike load testing - simulates sudden traffic spikes
    """
    
    wait_time = between(0.1, 0.5)  # Very fast requests to simulate spike
    
    @task
    def spike_requests(self):
        """Generate spike load"""
        endpoints = [
            "/api/v1/cryptocurrencies/",
            "/api/v1/cryptocurrencies/BTC",
            "/api/v1/cryptocurrencies/top/market_cap?limit=10"
        ]
        
        endpoint = random.choice(endpoints)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code in [200, 429, 503]:  # Accept various responses under load
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


if __name__ == "__main__":
    """
    Run locust from command line:
    
    # Basic load test
    locust -f app/tests/load/test_load.py --host=http://localhost:8000
    
    # Headless with specific users and duration
    locust -f app/tests/load/test_load.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 300s --headless
    
    # Heavy load test
    locust -f app/tests/load/test_load.py --host=http://localhost:8000 --users 500 --spawn-rate 50 --run-time 600s --headless HeavyLoadUser
    """
    import os
    os.system("locust --help")