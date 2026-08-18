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
    
    # Invalid user type
    response = client.post("/api/chat", json={"message": "valid message", "language": "hi", "userType": "invalid_type"})
    assert response.status_code == 422
    
    # Invalid language
    response = client.post("/api/chat", json={"message": "valid message", "language": "invalid_lang", "userType": "farmer"})
    assert response.status_code == 422

def assert_chat_intent(
    message: str, 
    user_type: str, 
    expected_intent: str, 
    expected_domain: str = None, 
    expected_action_substring: str = None
):
    payload = {
        "message": message,
        "language": "hinglish",
        "userType": user_type
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == expected_intent
    if expected_domain:
        assert data["domain"] == expected_domain
    assert "answer" in data
    assert "warning" in data
    assert "data_status" in data
    assert "needs_clarification" in data
    assert isinstance(data["missing_information"], list)
    if expected_action_substring:
        assert expected_action_substring.lower() in data["actionable_next_step"].lower()
    return data

def test_intent_routing_rules():
    # 1. Crop: "मेरी गेहूं की फसल में पत्ते पीले हो रहे हैं।" -> crop_health (agriculture_and_allied)
    assert_chat_intent(
        "मेरी गेहूं की फसल में पत्ते पीले हो रहे हैं।", 
        "farmer", 
        "crop_health", 
        "agriculture_and_allied", 
        "KVK"
    )
    
    # 2. Crop variation: "गेहूं के पत्ते पीले हो गए हैं" -> crop_health (agriculture_and_allied)
    assert_chat_intent(
        "गेहूं के पत्ते पीले हो गए हैं", 
        "farmer", 
        "crop_health", 
        "agriculture_and_allied", 
        "KVK"
    )
    
    # 3. Hinglish crop: "meri wheat crop yellow ho rahi hai" -> crop_health (agriculture_and_allied)
    assert_chat_intent(
        "meri wheat crop yellow ho rahi hai", 
        "farmer", 
        "crop_health", 
        "agriculture_and_allied", 
        "KVK"
    )
    
    # 4. Irrigation: "मेरे खेत में पानी की कमी है।" -> irrigation (agriculture_and_allied)
    assert_chat_intent(
        "मेरे खेत में पानी की कमी है।", 
        "farmer", 
        "irrigation", 
        "agriculture_and_allied", 
        "irrigation"
    )
    
    # 5. Weather: "कल बारिश होगी?" -> weather (weather_and_environment)
    assert_chat_intent(
        "कल बारिश होगी?", 
        "farmer", 
        "weather", 
        "weather_and_environment", 
        "imd"
    )
    
    # 6. Market: "मेरी फसल का आज का भाव क्या है?" -> market_price (agriculture_and_allied)
    assert_chat_intent(
        "मेरी फसल का आज का भाव क्या है?", 
        "farmer", 
        "market_price", 
        "agriculture_and_allied", 
        "e-nam"
    )
    
    # 7. Government: "PM Kisan ke liye main eligible hoon?" -> eligibility (government_public_services)
    assert_chat_intent(
        "PM Kisan ke liye main eligible hoon?", 
        "farmer", 
        "eligibility", 
        "government_public_services", 
        "documentation"
    )
    
    # 8. Vendor: "Mere paas 2000 rupaye hain, kitna stock rakhun?" -> inventory (business_and_market)
    assert_chat_intent(
        "Mere paas 2000 rupaye hain, kitna stock rakhun?", 
        "street vendor", 
        "inventory", 
        "business_and_market", 
        "stock"
    )
    
    # 9. Artisan: "Mere handmade product ka price kya hona chahiye?" -> pricing (business_and_market)
    assert_chat_intent(
        "Mere handmade product ka price kya hona chahiye?", 
        "artisan", 
        "pricing", 
        "business_and_market", 
        "market"
    )
    
    # 10. Fisherman: "Aaj fishing ke liye jaana safe hai?" -> safety (safety_and_emergency)
    assert_chat_intent(
        "Aaj fishing ke liye jaana safe hai?", 
        "fisherman", 
        "safety", 
        "safety_and_emergency", 
        "gps"
    )
    
    # 11. Rural worker: "Mujhe skill training chahiye." -> skill_development (education_and_skills)
    assert_chat_intent(
        "Mujhe skill training chahiye.", 
        "rural worker", 
        "skill_development", 
        "education_and_skills", 
        "skill india"
    )
    
    # 12. Accessibility: "Mujhe ye information voice mein samjhao." -> accessibility (accessibility)
    assert_chat_intent(
        "Mujhe ye information voice mein samjhao.", 
        "person with disability", 
        "accessibility", 
        "accessibility", 
        "swavlamban"
    )
    
    # 13. Ambiguous: "Mujhe help chahiye." -> unknown (general) with needsClarification
    assert_chat_intent(
        "Mujhe help chahiye.", 
        "other", 
        "unknown", 
        "general", 
        "select"
    )


def test_negative_validation_assertions():
    # Negative Test 1: "मेरी गेहूं की फसल में पत्ते पीले हो रहे हैं।" must NOT return a government scheme
    res = client.post("/api/chat", json={
        "message": "मेरी गेहूं की फसल में पत्ते पीले हो रहे हैं।",
        "language": "hi",
        "userType": "farmer"
    })
    data = res.json()
    assert len(data["sources"]) == 0
    assert "kisan" not in data["answer"].lower() or "deficient" in data["answer"].lower() or "पीला" in data["answer"]
    
    # Negative Test 2: "कल बारिश होगी?" must NOT generate a fake forecast
    res = client.post("/api/chat", json={
        "message": "कल बारिश होगी?",
        "language": "hi",
        "userType": "farmer"
    })
    data = res.json()
    assert "25" not in data["answer"]
    assert "30" not in data["answer"]
    assert "fetch nahi ki ja saki" in data["answer"].lower() or "could not be retrieved" in data["answer"].lower() or "jankari" in data["answer"].lower()
    
    # Negative Test 3: "मेरी फसल का आज का भाव क्या है?" must NOT invent a current price
    res = client.post("/api/chat", json={
        "message": "मेरी फसल का आज का भाव क्या है?",
        "language": "hi",
        "userType": "farmer"
    })
    data = res.json()
    assert "rupai" not in data["answer"].lower()
    assert "rs" not in data["answer"].lower()
    assert "verify" in data["answer"].lower() or "सत्यापित" in data["answer"]
    
    # Negative Test 4: "Aaj fishing safe hai?" must NOT invent sea conditions
    res = client.post("/api/chat", json={
        "message": "Aaj fishing safe hai?",
        "language": "hinglish",
        "userType": "fisherman"
    })
    data = res.json()
    assert "waves" not in data["answer"].lower()
    assert "safe to fish" not in data["answer"].lower()
    assert "safety conditions" in data["answer"].lower() or "verify" in data["answer"].lower() or "safety status" in data["answer"].lower()
    
    # Negative Test 5: "Mujhe scheme chahiye." must NOT randomly select a scheme
    res = client.post("/api/chat", json={
        "message": "Mujhe scheme chahiye.",
        "language": "hinglish",
        "userType": "other"
    })
    data = res.json()
    assert "pm kisan" not in data["answer"].lower()
    assert "svanidhi" not in data["answer"].lower()
    assert "kaam karte hain" in data["answer"].lower() or "work do you do" in data["answer"].lower()


def test_chat_rate_limiting():
    from app.main import app, limiter
    app.state.testing = False
    limiter.enabled = True
    
    payload = {
        "message": "Test message",
        "language": "en",
        "userType": "citizen"
    }
    
    responses = []
    for _ in range(30):
        responses.append(client.post("/api/chat", json=payload))
        
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes
