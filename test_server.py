import requests
import json

def test_chat():
    print("Testing /chat endpoint...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": "Hello, are you working?"}
        )
        if response.status_code == 200:
            print("Success!")
            print("Response:", response.json())
        else:
            print(f"Failed with status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_chat()
