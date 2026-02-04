"""Quick script to check ERPNext configuration and test connection."""
from app.config import Config
import requests

print("=" * 50)
print("ERPNext Configuration Check")
print("=" * 50)
print(f"ERPNEXT_BASE_URL: {Config.ERPNEXT_BASE_URL}")
print(f"ERPNEXT_API_KEY set: {'Yes' if Config.ERPNEXT_API_KEY else 'No'}")
print(f"ERPNEXT_API_SECRET set: {'Yes' if Config.ERPNEXT_API_SECRET else 'No'}")
print(f"Configuration valid: {Config.validate_erpnext_config()}")
print("=" * 50)

if not Config.validate_erpnext_config():
    print("\n⚠️  ERPNext is NOT configured!")
    print("\nTo configure, set these environment variables:")
    print("  ERPNEXT_BASE_URL=http://localhost:8080")
    print("  ERPNEXT_API_KEY=your_api_key")
    print("  ERPNEXT_API_SECRET=your_api_secret")
    print("\nThen restart the server with: python run.py")
else:
    print("\n✓ ERPNext is configured correctly!")
    
    # Test connection
    print("\n" + "=" * 50)
    print("Testing ERPNext Connection...")
    print("=" * 50)
    try:
        url = f"{Config.ERPNEXT_BASE_URL.rstrip('/')}/api/resource/User"
        headers = {
            'Authorization': f'token {Config.ERPNEXT_API_KEY}:{Config.ERPNEXT_API_SECRET}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✓ Connection successful! ERPNext is reachable.")
        else:
            print(f"⚠️  Connection returned status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection failed: Cannot reach ERPNext at {Config.ERPNEXT_BASE_URL}")
        print(f"  Make sure ERPNext is running on that address.")
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)}")