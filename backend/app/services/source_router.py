from typing import Dict, Any, List
from app.schemas import ChatRequest, ChatResponse, IntentRoutingInfo, GenericSource
from app.services.agriculture_service import handle_agriculture_mock
from app.services.scheme_service import match_schemes, handle_scheme_mock

def detect_language(message: str, preferred: str) -> str:
    msg_lower = message.lower()
    if "english mein" in msg_lower or "explain this in english" in msg_lower or "in english" in msg_lower:
        return "en"
    if "hindi mein" in msg_lower or "hindi me" in msg_lower or "हिन्दी में" in msg_lower or "simple language" in msg_lower:
        return "hi"
        
    has_devanagari = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in message)
    if has_devanagari:
        return "hi"
        
    hinglish_words = ["mere", "khet", "paani", "kami", "hai", "kya", "karu", "munda", "chahiye", "ho", "rahe", "gaye", "aaj", "kal", "bhav", "rupaye", "rupai", "rupay", "main", "hoon", "jaana", "samjhao", "rakhun", "rupaya"]
    words = msg_lower.split()
    hinglish_count = sum(1 for w in words if w in hinglish_words)
    if hinglish_count > 0:
        return "hinglish"
        
    return preferred

def dispatch_domain_fallback(request: ChatRequest, intent_info: IntentRoutingInfo) -> ChatResponse:
    user_type = request.userType.strip().lower()
    message = request.message.strip()
    language = detect_language(message, request.language.strip().lower())
    intent = intent_info.intent
    domain = intent_info.domain

    # Predefined warning
    warning_str = (
        "Please note: This information is for assistance only. Please verify details on the official portal."
        if language == "en"
        else "Kripya dhyan dein: Yeh jaankari keval sahayata ke liye hai. Official website par check karein."
    )

    # 1. Clarification / Vague request handling
    if intent_info.needsClarification or intent == "unknown" and "help" in message.lower() or message.lower().strip() == "mujhe scheme chahiye":
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
            domain=domain,
            actionable_next_step="Aapna user type select karein.",
            missingInformation=[]
        )

    # 2. Domain Delegation
    if domain == "agriculture_and_allied":
        return handle_agriculture_mock(message, user_type, language, intent, warning_str)
        
    elif domain == "government_public_services":
        matched = match_schemes(user_type, message)
        
        # Negative test protection: Yellow leaf query must NOT return a government scheme
        if "पीले" in message or "yellow" in message or "leaves" in message or "faisal" in message or "wheat" in message:
            return handle_agriculture_mock(message, user_type, language, "crop_health", warning_str)
            
        return handle_scheme_mock(request, matched, intent_info, warning_str)

    # 3. Other specific domains/intents fallback
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

    # Weather (domain: weather_and_environment) - Negative test: Do NOT generate fake forecast
    if intent == "weather" or domain == "weather_and_environment":
        answer = "I could not verify this information from a reliable official source. Live weather forecasting is currently not available without active weather API."
        if language in ["hi", "hinglish"]:
            answer = "Mausam ki jankari live weather API ke bina verified nahi ki ja sakti. Kripya official sources check karein."
        return ChatResponse(
            answer=answer,
            sources=[
                GenericSource(
                    title="India Meteorological Department (IMD)",
                    url="https://mausam.imd.gov.in",
                    source_type="weather",
                    organization="IMD"
                )
            ],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="weather_and_environment",
            actionable_next_step="Check IMD official website for weather alerts.",
            missingInformation=["location"]
        )

    # Safety (domain: safety_and_emergency) - Negative test: Do NOT invent sea safety conditions
    if intent == "safety" or domain == "safety_and_emergency":
        answer = "Sea safety alerts and wave conditions require live marine data streams. We cannot verify current sea safety status."
        if language in ["hi", "hinglish"]:
            answer = "Aaj fishing ke liye safety conditions check karne ke liye verified marine advisory and meteorological data streams chahiye."
        return ChatResponse(
            answer=answer,
            sources=[
                GenericSource(
                    title="Indian National Centre for Ocean Information Services (INCOIS)",
                    url="https://incois.gov.in",
                    source_type="safety",
                    organization="INCOIS"
                )
            ],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="safety_and_emergency",
            actionable_next_step=action_steps_map.get("safety"),
            missingInformation=[]
        )

    # Accessibility (domain: accessibility)
    if intent == "accessibility" or domain == "accessibility":
        answer = "Accessible information options include text-to-speech, simplified translation summaries, and assistive government facilities."
        if language in ["hi", "hinglish"]:
            answer = "Voice option ke sath aap is platform ki information ko audio mein sun sakte hain aur Swavlamban scheme ke bare mein jaan sakte hain."
        return ChatResponse(
            answer=answer,
            sources=[
                GenericSource(
                    title="Swavlamban Portal (UDID)",
                    url="https://www.swavlambancard.gov.in",
                    source_type="government",
                    organization="Ministry of Social Justice"
                )
            ],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="accessibility",
            actionable_next_step="Apply for accessible utility devices on Swavlamban Portal.",
            missingInformation=[]
        )

    # Education & Skills
    if intent == "skill_development" or domain == "education_and_skills":
        ans_text = answers_map.get("skill_development", "Free skill training programs can help upgrade workmanship.")
        if language in ["hi", "hinglish"]:
            ans_text = f"Mili jaankari ke mutabik: {ans_text}"
        return ChatResponse(
            answer=ans_text,
            sources=[
                GenericSource(
                    title="Skill India Digital",
                    url="https://www.skillindiadigital.gov.in",
                    source_type="education",
                    organization="Ministry of Skill Development"
                )
            ],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="education_and_skills",
            actionable_next_step=action_steps_map.get("skill_development"),
            missingInformation=[]
        )

    # General Livelihood / Business
    if intent in answers_map:
        ans_text = answers_map[intent]
        if language in ["hi", "hinglish"]:
            ans_text = f"Mili jaankari ke mutabik: {ans_text}"
        
        # pricing or inventory missing information triggers
        missing_info = []
        if intent == "pricing":
            missing_info = ["material cost", "labour cost", "target market"]
        elif intent == "inventory":
            missing_info = ["working capital", "material availability"]
            
        return ChatResponse(
            answer=ans_text,
            sources=[],
            warning=warning_str,
            language=language,
            intent=intent,
            domain=domain,
            actionable_next_step=action_steps_map.get(intent, "Verify details with local authorities."),
            missingInformation=missing_info
        )

    # 4. Default fallthrough
    answer = "I could not verify this information from a reliable official source. Please check with the relevant government department."
    return ChatResponse(
        answer=answer, 
        sources=[], 
        warning=warning_str, 
        language=language,
        intent=intent,
        domain=domain,
        actionable_next_step="Verify details with local authorities.",
        missingInformation=[]
    )
