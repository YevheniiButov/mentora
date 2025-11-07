#!/usr/bin/env python3
"""
Diagnostic script to check routes on running Flask server
Run this while Flask server is running to see what routes are registered
"""
import requests
import sys

BASE_URL = 'http://127.0.0.1:5002'

def check_route_info():
    """Check what routes are available"""
    print("=== Route Diagnostics ===\n")
    
    # Test simple routes
    test_routes = [
        '/uk/',
        '/en/',
        '/ru/',
        '/nl/',
    ]
    
    for route in test_routes:
        try:
            url = f"{BASE_URL}{route}"
            response = requests.get(url, allow_redirects=False, timeout=2)
            print(f"{route}:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            print(f"  Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 404:
                content = response.text[:200]
                if '404' in content or 'Page Not Found' in content:
                    print(f"  → Custom 404 page")
                else:
                    print(f"  → Flask default 404")
            elif response.status_code == 302:
                print(f"  → Redirect to: {response.headers.get('Location', 'unknown')}")
            elif response.status_code == 200:
                content = response.text[:100]
                if '<html' in content or '<!DOCTYPE' in content:
                    print(f"  → HTML page (first 100 chars: {content})")
                else:
                    print(f"  → Non-HTML response")
            print()
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {BASE_URL}")
            print("   Make sure Flask server is running on port 5002")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error checking {route}: {e}")
            print()

if __name__ == '__main__':
    check_route_info()


