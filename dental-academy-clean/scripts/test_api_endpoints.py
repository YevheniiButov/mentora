#!/usr/bin/env python3
"""
Test script for API endpoints
"""

import requests
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing API endpoints...")
    
    # Test 1: Check if daily-learning blueprint is accessible
    print("\n1. Testing daily-learning blueprint registration...")
    try:
        response = requests.get(f"{base_url}/daily-learning/learning-map", allow_redirects=False)
        print(f"   /daily-learning/learning-map: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Blueprint registered correctly (redirect to login expected)")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check API endpoint directly
    print("\n2. Testing API endpoint directly...")
    try:
        response = requests.post(
            f"{base_url}/daily-learning/api/daily-plan/mark-completed",
            json={"content_id": 1, "content_type": "lesson"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   /daily-learning/api/daily-plan/mark-completed: {response.status_code}")
        if response.status_code in [401, 403]:
            print("   ✅ Endpoint exists (auth required)")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check old URL (should fail)
    print("\n3. Testing old URL (should fail)...")
    try:
        response = requests.post(
            f"{base_url}/api/daily-plan/mark-completed",
            json={"content_id": 1, "content_type": "lesson"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   /api/daily-plan/mark-completed: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Old URL correctly returns 404")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check other daily-learning endpoints
    print("\n4. Testing other daily-learning endpoints...")
    endpoints = [
        "/daily-learning/api/study-session/1/complete",
        "/daily-learning/api/session/answer",
        "/daily-learning/api/session/complete"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", allow_redirects=False)
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: ❌ Error: {e}")
    
    print("\n✅ API endpoint testing completed!")

if __name__ == "__main__":
    test_api_endpoints() 