import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_subscribe():
    url = f"{BASE_URL}/subscribe"
    payload = {"email": "tester@example.com"}
    response = requests.post(url, json=payload)
    print(f"Subscribe response: {response.status_code} - {response.text}")

def test_briefing():
    url = f"{BASE_URL}/briefing"
    response = requests.get(url)
    print(f"Briefing response: {response.status_code}")

if __name__ == "__main__":
    test_subscribe()
    test_briefing()
