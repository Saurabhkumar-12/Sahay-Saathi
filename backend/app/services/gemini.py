import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.schemas import ChatRequest, ChatResponse, SchemeSource, IntentRoutingInfo
from app.services.router import route_intent
from app.services.scheme_service import match_schemes

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return None
    return genai.Client(api_key=api_key)

async def generate_assistance(request: ChatRequest) -> ChatResponse:
    user_type = request.userType.strip().lower()
    message = request.message.strip()
    language = request.language.strip().lower()
    
    # 1. Route Intent & Domain
    routing_info = await route_intent(message, user_type)
    
    # 2. Setup match schemes if intent is scheme/eligibility related
    matched = []
    if routing_info.intent in ["government_scheme", "eligibility", "documents", "application_process"]:
        matched = match_schemes(user_type, message)
        
    # 3. Setup Gemini client
    client = get_gemini_client()
    
    # Fallback/Mock Mode if API key is missing or invalid
    if not client:
        return handle_mock_fallback(request, matched, routing_info)
        
    schemes_context = ""
    if matched:
        schemes_context = json.dumps(matched, indent=2)
    else:
        schemes_context = "No specific scheme matches found."
        
    system_instruction = f"""You are Sahay Saathi, an empathetic AI-powered citizen assistance platform for underserved communities in India.
Your goal is to understand the user's problem first, then provide the most relevant assistance based on their context, intent, and domain.

CONTEXT:
User Type: {user_type}
Preferred Language: {language}
Classified Intent: {routing_info.intent}
Classified Domain: {routing_info.domain}

SCHEME REFERENCE DATA:
{schemes_context}

RULES:
1. Intent & Domain Awareness: The intent is "{routing_info.intent}" and domain is "{routing_info.domain}". Ground your answer in this intent/domain. Do not recommend government schemes unless the intent is scheme-related.
2. Problem-First Approach:
   - For non-government queries (e.g. crop health, irrigation, weather, safety, livelihood, pricing, stock decisions): Provide helpful domain-specific guidance. Do not force the response to mention government schemes.
   - For Crop Health queries (e.g. yellow leaves):
     * Explain that symptoms can have multiple possible causes.
     * Cautious Phrasing: Use words like "Possible causes include..." instead of "Your crop has...". Do not make a definitive diagnosis.
     * Ask missing questions: crop age, location, leaf location (lower or upper), irrigation status, and recent fertilizers.
     * Offer safe immediate precautions (e.g. ensure drainage, avoid applying excess fertilizers until confirmed).
     * Request photos/details.
     * Recommend consulting a local agricultural expert or Krishi Vigyan Kendra (KVK).
     * Do not prescribe specific chemical dosages unless supported by official documents.
3. Verification & Hallucination:
   - For government queries, rely on official government sources.
   - For agricultural/livelihood queries, use reliable domain sources.
   - If the query requires live data (weather forecasts, real-time crop/market prices, live sea safety conditions) and needsLiveData=true, you must state that you cannot verify this live information without real-time connection. Do not fabricate forecast, prices, or conditions.
4. Ambiguity: If needsClarification is true, ask a clarifying question about their specific profession or situation.
5. Provide response in the requested language (en, hi, or hinglish).
6. Output JSON matching the schema (with fields: answer, sources, warning, language, intent, domain, actionable_next_step).
"""

    try:
        # Call Gemini using Structured JSON output matching ChatResponse schema
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=message,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChatResponse,
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        # Parse the structured JSON response
        response_data = json.loads(response.text)
        return ChatResponse(**response_data)
        
    except APIError as e:
        print(f"Gemini API Error: {e}")
        return handle_mock_fallback(request, matched, routing_info)
    except Exception as e:
        print(f"Unexpected error calling Gemini: {e}")
        return handle_mock_fallback(request, matched, routing_info)

def handle_mock_fallback(request: ChatRequest, matched: List[Dict[str, Any]], intent_info: IntentRoutingInfo) -> ChatResponse:
    from app.services.source_router import dispatch_domain_fallback
    return dispatch_domain_fallback(request, intent_info)
