"""
Test the backend API endpoints
Simple test script to verify the FastAPI backend is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_ping():
    """Test ping endpoint"""
    print("Testing ping endpoint...")
    response = requests.get(f"{BASE_URL}/ping")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_get_users():
    """Test get users endpoint"""
    print("Testing get users endpoint...")
    response = requests.get(f"{BASE_URL}/users/")
    print(f"Status: {response.status_code}")
    users = response.json()
    print(f"Found {len(users)} users")
    if users:
        print(f"First user: {users[0]}\n")


def test_get_images():
    """Test get images endpoint"""
    print("Testing get images endpoint...")
    response = requests.get(f"{BASE_URL}/images/")
    print(f"Status: {response.status_code}")
    images = response.json()
    print(f"Found {len(images)} images")
    if images:
        print(f"First image: {images[0]}\n")


def test_search_labels():
    """Test label search endpoint"""
    print("Testing label search endpoint...")
    response = requests.get(f"{BASE_URL}/labels/search?label=person")
    print(f"Status: {response.status_code}")
    results = response.json()
    print(f"Found {len(results)} images with label 'person'")
    if results:
        print(f"First result: {results[0]}\n")


if __name__ == "__main__":
    print("=== ImageLab Backend API Tests ===")
    
    try:
        test_root()
        test_ping()
        test_get_users()
        test_get_images()
        test_search_labels()
        
        print("=== All tests completed ===")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"ERROR: {e}")
