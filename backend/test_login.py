import requests

try:
    response = requests.post("http://127.0.0.1:5000/api/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
