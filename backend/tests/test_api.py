import pytest
from fastapi.testclient import TestClient
import os
import sys

# Disable real Gemini API during automated tests to enforce mock predictability and avoid quota issues
os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_invalid_requests():
    # Empty message
    response = client.post("/api/chat", json={"message": "   ", "language": "hi", "userType": "farmer"})
    assert response.status_code == 422
    
    # Invalid language
    response = client.post("/api/chat", json={"message": "Hello", "language": "french", "userType": "farmer"})
    assert response.status_code == 422
    
    # Invalid userType
    response = client.post("/api/chat", json={"message": "Hello", "language": "en", "userType": "architect"})
    assert response.status_code == 422

# Map helper to execute tests and assert classified intent
def assert_chat_intent(message: str, user_type: str, expected_intent: str, expected_action_substring: str = None):
    payload = {
        "message": message,
        "language": "hinglish",
        "userType": user_type
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == expected_intent
    assert "answer" in data
    assert "warning" in data
    if expected_action_substring:
        assert expected_action_substring.lower() in data["actionable_next_step"].lower()

def test_intent_routing_rules():
    # 1. Farmer + PM Kisan -> eligibility / government_scheme
    assert_chat_intent("PM Kisan ke liye kaun eligible hai?", "farmer", "eligibility", "documentation")
    assert_chat_intent("Mujhe PM Kisan scheme ke baare mein bataiye", "farmer", "government_scheme", "official website")
    
    # 2. Farmer + water shortage -> irrigation
    assert_chat_intent("Farming ke liye water shortage hai", "farmer", "irrigation", "irrigation")
    
    # 3. Farmer + rain -> weather
    assert_chat_intent("Will it rain tomorrow?", "farmer", "weather", "imd")
    
    # 4. Farmer + crop disease -> crop_health
    assert_chat_intent("Crop disease treatment kya hai?", "farmer", "crop_health", "extension")
    
    # 5. Farmer + crop price -> market_price
    assert_chat_intent("What is today's crop price?", "farmer", "market_price", "e-nam")
    
    # 6. Street Vendor + government loan -> financial_support
    assert_chat_intent("Mere liye government loan scheme kya hai?", "street vendor", "financial_support", "banks")
    
    # 7. Street Vendor + stock decision -> inventory
    assert_chat_intent("How much stock should I keep today?", "street vendor", "inventory", "stock")
    
    # 8. Artisan + product pricing -> pricing
    assert_chat_intent("How to determine product pricing?", "artisan", "pricing", "market")
    
    # 9. Artisan + selling online -> market_access
    assert_chat_intent("Can I start selling online?", "artisan", "market_access", "ondc")
    
    # 10. Fisherman + sea safety -> safety
    assert_chat_intent("Is sea safety guaranteed today?", "fisherman", "safety", "gps")
    
    # 11. Rural Worker + skill training -> skill_development
    assert_chat_intent("How to get skill training?", "rural worker", "skill_development", "skill india")
    
    # 12. Person with Disability + accessible service -> accessibility
    assert_chat_intent("Where can I find accessible utility devices?", "person with disability", "accessibility", "swavlamban")
    
    # 13. Citizen + pension -> government_service
    assert_chat_intent("Widow pension eligibility check", "citizen", "government_service", "government")
    
    # 14. Emergency Safety
    assert_chat_intent("Mujhe safety ke liye help chahiye", "citizen", "emergency_help", "112")
    
    # 15. Ambiguous query -> clarified
    assert_chat_intent("Mujhe scheme chahiye.", "other", "unknown", "select")
    
    # 16. Out-of-scope / Unknown
    assert_chat_intent("Tomorrow stock market mein kya hoga?", "citizen", "unknown", "authorities")

def test_chat_rate_limiting():
    from app.main import app, limiter
    app.state.testing = False
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
