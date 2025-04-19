import requests
try:
    response = requests.get("https://testnet-api.4160.nodely.dev")
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")