#!/usr/bin/env python3
"""
Test script to check if routes are working correctly
Run this while Flask server is running
"""
import requests
import sys

BASE_URL = 'http://127.0.0.1:5002'

def test_route(path, expected_status=200):
    """Test a single route"""
    try:
        url = f"{BASE_URL}{path}"
        response = requests.get(url, allow_redirects=False, timeout=5)
        status = response.status_code
        
        if status == expected_status:
            print(f"✅ {path}: {status}")
            return True
        elif status == 302:
            print(f"🔄 {path}: {status} -> {response.headers.get('Location', 'unknown')}")
            return True  # Redirect is acceptable
        else:
            print(f"❌ {path}: {status} (expected {expected_status})")
            if status == 404:
                print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {path}: Cannot connect to server. Is Flask running on {BASE_URL}?")
        return False
    except Exception as e:
        print(f"❌ {path}: Error - {e}")
        return False

if __name__ == '__main__':
    print("=== Testing Flask Routes ===\n")
    
    routes = [
        ('/uk/', 200),
        ('/en/', 200),
        ('/ru/', 200),
        ('/nl/', 200),
        ('/en/learning-map', 302),  # Redirect to login
        ('/en/knowledge-base', 302),  # Redirect to login
        ('/en/community', 302),  # Redirect to login
        ('/en/big-info', 200),
    ]
    
    results = []
    for path, expected in routes:
        results.append(test_route(path, expected))
    
    print(f"\n=== Results: {sum(results)}/{len(results)} passed ===")
    
    if all(results):
        print("✅ All routes working correctly!")
        sys.exit(0)
    else:
        print("❌ Some routes are not working")
        sys.exit(1)


