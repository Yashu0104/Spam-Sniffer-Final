#!/usr/bin/env python3
"""
Test script to verify Spam Sniffer setup
"""

import requests
import time
import sys

def test_backend_health():
    """Test if the backend is running and healthy"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_spam_detection():
    """Test the spam detection functionality"""
    try:
        test_text = "Get rich quick! Make money fast with this amazing offer!"
        response = requests.post(
            "http://localhost:5000/check_spam",
            json={"text": test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Spam detection working - Score: {data.get('spam_score', 'N/A')}")
            return True
        else:
            print(f"❌ Spam detection failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing spam detection: {e}")
        return False

def test_frontend_access():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    print("🧪 Testing Spam Sniffer Setup")
    print("=" * 40)
    
    # Wait a bit for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Spam Detection", test_spam_detection),
        ("Frontend Access", test_frontend_access),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Spam Sniffer is working correctly.")
        print("\n🌐 Access your application:")
        print("   Frontend: http://localhost:5173")
        print("   Backend API: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Check the logs and configuration.")
        print("\n📝 Troubleshooting tips:")
        print("   1. Run: docker-compose logs")
        print("   2. Check if all containers are running: docker-compose ps")
        print("   3. Restart services: docker-compose down && docker-compose up --build")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
