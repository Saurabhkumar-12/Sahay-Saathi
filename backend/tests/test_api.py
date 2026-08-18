import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_valid_request():
    payload = {
        "message": "PM Kisan ke liye kaun eligible hai?",
        "language": "hi",
        "userType": "farmer"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "warning" in data
    assert data["language"] == "hi"

def test_chat_empty_message():
    payload = {
        "message": "   ",
        "language": "hi",
        "userType": "farmer"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422
    assert "value_error" in response.text or "Value error" in response.text

def test_chat_invalid_language():
    payload = {
        "message": "Hello",
        "language": "spanish",
        "userType": "farmer"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422

def test_chat_invalid_user_type():
    payload = {
        "message": "Hello",
        "language": "en",
        "userType": "developer"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422

def test_chat_out_of_scope():
    payload = {
        "message": "Tomorrow stock market mein kya hoga?",
        "language": "en",
        "userType": "citizen"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "could not verify" in data["answer"].lower()
    assert len(data["sources"]) == 0

def test_chat_ambiguous():
    payload = {
        "message": "Mujhe scheme chahiye.",
        "language": "hi",
        "userType": "other"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "kaam karte hain" in data["answer"].lower() or "work do you do" in data["answer"].lower()
    assert len(data["sources"]) == 0

def test_chat_rate_limiting():
    from app.main import limiter
    limiter.enabled = True
    
    payload = {
        "message": "Test message",
        "language": "en",
        "userType": "citizen"
    }
    
    # Send multiple requests quickly to trigger 429
    responses = []
    for _ in range(30):
        responses.append(client.post("/api/chat", json=payload))
        
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes
