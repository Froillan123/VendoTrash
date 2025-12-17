"""
Quick script to get JWT token for ESP32-CAM
"""
import requests
import json
import sys

def get_token(email: str, password: str, server_url: str = "http://localhost:8000"):
    """Get JWT token from login endpoint"""
    try:
        response = requests.post(
            f"{server_url}/api/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("\n" + "="*60)
                print("✅ JWT Token Retrieved Successfully!")
                print("="*60)
                print(f"\nToken: {token}")
                print("\n" + "="*60)
                print("Copy this token and paste it in ESP32 code:")
                print("="*60)
                print(f'\nconst char* authToken = "{token}";\n')
                return token
            else:
                print("❌ No access_token in response")
                print(f"Response: {json.dumps(data, indent=2)}")
                return None
        else:
            print(f"❌ Login failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print(f"   Make sure server is running: python Server/main.py")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("ESP32-CAM JWT Token Getter")
    print("="*60)
    
    # Default credentials (admin user from seed_db.py)
    default_email = "admin@vendotrash.com"
    default_password = "admin123"
    
    print(f"\nUsing default admin credentials:")
    print(f"   Email: {default_email}")
    print(f"   Password: {default_password}")
    
    print("\nIf you want to use different credentials, edit this script.")
    print("\nConnecting to server...")
    
    token = get_token(default_email, default_password)
    
    if not token:
        print("\n💡 Alternative: Get token from web app:")
        print("   1. Open http://localhost:5175")
        print("   2. Login")
        print("   3. Press F12 → Network tab")
        print("   4. Click any API request")
        print("   5. Check Headers → Authorization: Bearer TOKEN")
        sys.exit(1)


