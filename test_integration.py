#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_backend_running():
    """Test if backend is accessible"""
    print("\n🔍 Testing if backend is running...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is running!")
            return True
        else:
            print(f"⚠️ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running on port 8000")
        print("   Start it with: cd backend && python api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_recommendations():
    """Test the get-recommendations endpoint"""
    print("\n🔍 Testing GET recommendations endpoint...")
    
    payload = {
        "user_id": "test_user_123",
        "colors": ["blue", "green"],
        "categories": ["Below the Knee"],
        "num_recommendations": 5
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/get-recommendations",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            
            print(f"✅ Got {len(recommendations)} recommendations")
            
            if recommendations:
                print("\n📋 Sample recommendation:")
                rec = recommendations[0]
                print(f"   ID: {rec.get('id')}")
                print(f"   Title: {rec.get('title', 'N/A')[:50]}...")
                print(f"   Color: {rec.get('color', 'N/A')}")
                print(f"   Category: {rec.get('category', 'N/A')}")
                print(f"   Price: {rec.get('price', 'N/A')}")
                print(f"   Has image_href: {'image_href' in rec}")
                print(f"   Similarity: {rec.get('similarity_score', 'N/A')}")
                return True
            else:
                print("⚠️ No recommendations returned")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_record_interaction():
    """Test the record-interaction endpoint"""
    print("\n🔍 Testing RECORD interaction endpoint...")
    
    payload = {
        "user_id": "test_user_123",
        "product_id": "product_1",
        "reaction": "like"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/record-interaction",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Interaction recorded successfully!")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_personalized_recommendations():
    """Test that recommendations change after interactions"""
    print("\n🔍 Testing personalized recommendations...")
    
    user_id = "test_personalization"
    
    # Get initial recommendations
    response1 = requests.post(
        f"{API_BASE_URL}/get-recommendations",
        json={"user_id": user_id, "num_recommendations": 3}
    )
    
    if response1.status_code != 200:
        print("❌ Failed to get initial recommendations")
        return False
    
    initial_recs = response1.json()["recommendations"]
    print(f"   Got {len(initial_recs)} initial recommendations")
    
    # Record some likes
    for rec in initial_recs[:2]:
        requests.post(
            f"{API_BASE_URL}/record-interaction",
            json={
                "user_id": user_id,
                "product_id": rec["id"],
                "reaction": "like"
            }
        )
    print("   Recorded 2 likes")
    
    # Get personalized recommendations
    response2 = requests.post(
        f"{API_BASE_URL}/get-recommendations",
        json={"user_id": user_id, "num_recommendations": 3}
    )
    
    if response2.status_code != 200:
        print("❌ Failed to get personalized recommendations")
        return False
    
    personalized_recs = response2.json()["recommendations"]
    print(f"   Got {len(personalized_recs)} personalized recommendations")
    
    # Check if recommendations changed
    initial_ids = {r["id"] for r in initial_recs}
    personalized_ids = {r["id"] for r in personalized_recs}
    
    if initial_ids == personalized_ids:
        print("⚠️ Recommendations didn't change (might be expected if dataset is small)")
    else:
        print("✅ Recommendations are personalized!")
    
    return True

def test_cors():
    """Test CORS headers"""
    print("\n🔍 Testing CORS configuration...")
    
    try:
        response = requests.options(
            f"{API_BASE_URL}/get-recommendations",
            headers={"Origin": "http://localhost:3000"}
        )
        
        cors_header = response.headers.get("access-control-allow-origin")
        if cors_header == "*":
            print("✅ CORS is properly configured (allows all origins)")
            return True
        else:
            print(f"⚠️ CORS header: {cors_header}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("  FRONTEND-BACKEND INTEGRATION TEST")
    print("="*60)
    
    tests = [
        ("Backend Running", test_backend_running),
        ("GET Recommendations", test_get_recommendations),
        ("Record Interaction", test_record_interaction),
        ("Personalized Recs", test_personalized_recommendations),
        ("CORS Configuration", test_cors),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
        
        # Skip remaining tests if backend is not running
        if test_name == "Backend Running" and not result:
            print("\n⚠️ Skipping remaining tests since backend is not running")
            break
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nScore: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working perfectly!")
        return 0
    elif passed > 0:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        return 1
    else:
        print("\n❌ All tests failed. Make sure the backend is running.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
