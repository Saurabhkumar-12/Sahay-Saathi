import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.schemas import ChatRequest, ChatResponse, SchemeSource, IntentRoutingInfo
from app.services.router import route_intent

# Load knowledge base
DATA_DIR = Path(__file__).parent.parent.parent / "data"
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.json"

def load_knowledge_base() -> List[Dict[str, Any]]:
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return []

KNOWLEDGE_BASE = load_knowledge_base()

def match_schemes(user_type: str, message: str) -> List[Dict[str, Any]]:
    """
    Retrieves schemes that match the user category or have matching keywords.
    """
    matched = []
    message_lower = message.lower()
    
    # Keyword indicators for specific schemes
    keywords = {
        "pm_kisan": ["kisan", "farmer", "kheti", "land", "farming", "agriculture"],
        "pm_svanidhi": ["svanidhi", "vendor", "street", "loan", "rehar", "cart", "shop", "thela", "hawker"],
        "pm_vishwakarma": ["vishwakarma", "artisan", "carpenter", "blacksmith", "potter", "sculptor", "cobbler", "tailor", "craft"],
        "pmmsy": ["matsya", "sampada", "fish", "fisherman", "fishing", "boat", "aquaculture"],
        "mgnrega": ["nrega", "mgnrega", "rural", "employment", "job", "card", "wage", "labour", "work"],
        "udid": ["disability", "udid", "disabled", "divyang", "swavlamban", "card"],
        "pmsby": ["insurance", "bima", "suraksha", "accident", "coverage", "premium"]
    }

    for scheme in KNOWLEDGE_BASE:
        scheme_id = scheme.get("id", "")
        # Match by category
        category_match = user_type in scheme.get("target_users", [])
        
        # Match by keyword query
        kw_match = False
        if scheme_id in keywords:
            for kw in keywords[scheme_id]:
                if kw in message_lower:
                    kw_match = True
                    break
        
        if category_match or kw_match:
            matched.append(scheme)
            
    # Fallback to returning all schemes if no matches but user requested general assistance
    if not matched and "scheme" in message_lower:
        # Limit to avoid token cluttering
        return KNOWLEDGE_BASE[:3]
        
    return matched

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return None
    return genai.Client(api_key=api_key)

async def generate_assistance(request: ChatRequest) -> ChatResponse:
    user_type = request.userType.strip().lower()
    message = request.message.strip()
    language = request.language.strip().lower()
    
    # 1. Route Intent
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
Your goal is to understand the user's problem first, then provide the most relevant assistance based on their context and intent.

CONTEXT:
User Type: {user_type}
Preferred Language: {language}
Classified Intent: {routing_info.intent}

SCHEME REFERENCE DATA:
{schemes_context}

RULES:
1. Intent Awareness: The intent classified is "{routing_info.intent}". Ground your answer in this intent. Do not recommend schemes unless the intent is specifically scheme-related (government_scheme, eligibility, documents, application_process).
2. Grounding & Hallucination:
   - For scheme details, only use the provided SCHEME REFERENCE DATA.
   - If the intent requires live data (weather, market_price, sea conditions, deadlines) and is marked as needsLiveData=true, you must state: "I could not verify this information from a reliable official source. Please check with the relevant government department." Do not fabricate live data.
3. Ambiguity: If needsClarification is true, ask a clear clarifying question about their specific profession or situation.
4. Actionable Next Step: Propose a direct, user-friendly next action.
5. Provide response in the requested language:
   - "hi" (Hindi): write simple, conversational Hindi using the Devanagari script.
   - "hinglish": write Hindi words using the Latin script (English letters), e.g., "Aap is scheme ke liye eligible hain agar...".
   - "en" (English): write simple, clear English.
6. The response must match the required JSON structure with fields:
   - "answer": the generated response text.
   - "sources": list of source schemes used from the provided data (include name, url, last_verified). Leave empty if not grounded.
   - "warning": Always set to: "Kripya dhyan dein: Yeh jaankari keval sahayata ke liye hai. Official application process ke liye official website par hi check karein." (or English equivalent: "Please note: This information is for assistance only. Please verify details on the official portal.").
   - "language": the language of the output (en, hi, or hinglish).
   - "intent": set to the classified intent.
   - "actionable_next_step": a clear instruction on what to do next.
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
    """
    Mock implementation for tests, missing keys, or rate-limited service issues.
    Matches predefined test cases from the project definition.
    """
    user_type = request.userType.strip().lower()
    message = request.message.strip()
    message_lower = message.lower()
    language = request.language.strip().lower()
    intent = intent_info.intent

    # Predefined local warning string
    warning_str = (
        "Please note: This information is for assistance only. Please verify details on the official portal."
        if language == "en"
        else "Kripya dhyan dein: Yeh jaankari keval sahayata ke liye hai. Official website par check karein."
    )

    # 1. Clarification check
    if intent_info.needsClarification:
        answer = (
            "Aap kis type ka kaam karte hain — farming, street vending, artisan work, fishing ya kuch aur?"
            if language in ["hi", "hinglish"]
            else "What type of work do you do? e.g., farming, street vending, artisan work, fishing, or something else?"
        )
        return ChatResponse(
            answer=answer, 
            sources=[], 
            warning=warning_str, 
            language=language,
            intent=intent,
            actionable_next_step="Aapna user type select karein."
        )

    # 2. Live Data / Hallucination Check
    if intent_info.needsLiveData:
        answer = "I could not verify this information from a reliable official source. Please check with the relevant government department."
        action_step = "Check official real-time portal for live updates."
        if intent == "weather":
            action_step = "Check IMD official website for weather alerts."
        elif intent == "market_price":
            action_step = "Check e-NAM portal for today's wholesale prices."
        return ChatResponse(
            answer=answer, 
            sources=[], 
            warning=warning_str, 
            language=language,
            intent=intent,
            actionable_next_step=action_step
        )

    # 3. Scheme-related intents
    if intent in ["government_scheme", "eligibility", "documents", "application_process"]:
        if matched:
            scheme = matched[0]
            sources = [SchemeSource(name=scheme["name"], url=scheme["official_source"], last_verified=scheme.get("last_verified"))]
            
            if intent == "eligibility":
                if language == "hi":
                    answer = f"**{scheme['name']}** ke liye eligibility criteria yeh hai: {scheme['eligibility']}"
                elif language == "hinglish":
                    answer = f"**{scheme['name']}** ke liye eligibility guidelines yeh hain: {scheme['eligibility']}"
                else:
                    answer = f"The eligibility criteria for **{scheme['name']}** is: {scheme['eligibility']}"
                action_step = "Gather identity proof and land/business documentation."
                
            elif intent == "documents":
                docs_str = ", ".join(scheme["required_documents"])
                if language == "hi":
                    answer = f"**{scheme['name']}** ke liye required documents: {docs_str}"
                elif language == "hinglish":
                    answer = f"**{scheme['name']}** ke liye zaroori documents: {docs_str}"
                else:
                    answer = f"Required documents for **{scheme['name']}**: {docs_str}"
                action_step = "Scan and save these documents on your mobile phone."
                
            elif intent == "application_process":
                steps_str = " -> ".join(scheme["application_steps"])
                if language == "hi":
                    answer = f"**{scheme['name']}** ka application process: {steps_str}"
                elif language == "hinglish":
                    answer = f"**{scheme['name']}** ka apply karne ka tareeqa: {steps_str}"
                else:
                    answer = f"Application process for **{scheme['name']}**: {steps_str}"
                action_step = f"Visit {scheme['official_source']} and apply online."
                
            else: # government_scheme
                if language == "hi":
                    answer = f"Aapke liye **{scheme['name']}** upyogi hai. {scheme['description']}"
                elif language == "hinglish":
                    answer = f"Aapke liye **{scheme['name']}** useful hai. {scheme['description']}"
                else:
                    answer = f"The **{scheme['name']}** is designed for you. {scheme['description']}"
                action_step = f"Read the full details on the official website: {scheme['official_source']}."
                
            return ChatResponse(
                answer=answer, 
                sources=sources, 
                warning=warning_str, 
                language=language,
                intent=intent,
                actionable_next_step=action_step
            )

    action_steps_map = {
        "irrigation": "Contact your local block agriculture or irrigation officer.",
        "crop_health": "Send a leaf photo to the local Kisan helpdesk or extension center.",
        "pricing": "Compare your wholesale prices in local markets before finalizing sale.",
        "inventory": "Update your physical stock registers daily to trace items.",
        "market_access": "Explore registering on the government-backed ONDC network.",
        "safety": "Keep emergency life jackets ready, keep GPS active, and monitor coastal advisory boards.",
        "skill_development": "Register on the Skill India Digital portal.",
        "accessibility": "Apply for accessible utility devices on Swavlamban Portal.",
        "government_service": "Visit your nearest local government administration office.",
        "emergency_help": "Call the national emergency helpline 112 immediately.",
        "financial_support": "Apply for standard interest-subsidized credit from local banks."
    }
    
    answers_map = {
        "irrigation": "Drought or water shortage controls require proper drip/sprinkler systems or borewell connections.",
        "crop_health": "Crop diseases should be treated using certified bio-pesticides recommended by agriculture officers.",
        "pricing": "Ensure your product pricing covers all materials, toolkit amortizations, and daily wages.",
        "inventory": "Maintain proper stock tracking to check which materials sell fastest and avoid over-stocking.",
        "market_access": "Selling online lets you reach customers across cities without middle agents.",
        "safety": "Please monitor local sea advisories and keep GPS navigation devices active on boats.",
        "skill_development": "Free skill training is provided by government centers to upgrade traditional workmanship.",
        "accessibility": "Accessible utility devices like wheelchairs, hearing aids, and UDID cards help divyangjan citizens.",
        "government_service": "Pensions and civic utilities can be processed via local municipality offices.",
        "emergency_help": "Immediate local security, medical, and disaster services are available by dialing 112.",
        "financial_support": "Financial support and low-interest business loans are available for street vendors."
    }

    if intent in answers_map:
        ans_text = answers_map[intent]
        if language in ["hi", "hinglish"]:
            ans_text = f"Mili jaankari ke mutabik: {ans_text}"
        return ChatResponse(
            answer=ans_text,
            sources=[],
            warning=warning_str,
            language=language,
            intent=intent,
            actionable_next_step=action_steps_map.get(intent, "Verify details with local authorities.")
        )

    # 5. Default/Unknown
    answer = "I could not verify this information from a reliable official source. Please check with the relevant government department."
    return ChatResponse(
        answer=answer, 
        sources=[], 
        warning=warning_str, 
        language=language,
        intent=intent,
        actionable_next_step="Verify details with local authorities."
    )
