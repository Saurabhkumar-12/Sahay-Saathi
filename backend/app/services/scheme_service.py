import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.schemas import ChatResponse, SchemeSource, ChatRequest, IntentRoutingInfo

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
    matched = []
    message_lower = message.lower()
    
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
        category_match = user_type in scheme.get("target_users", [])
        
        kw_match = False
        if scheme_id in keywords:
            for kw in keywords[scheme_id]:
                if kw in message_lower:
                    kw_match = True
                    break
        
        if category_match or kw_match:
            matched.append(scheme)
            
    if not matched and "scheme" in message_lower:
        return KNOWLEDGE_BASE[:3]
        
    return matched

def handle_scheme_mock(
    request: ChatRequest, 
    matched: List[Dict[str, Any]], 
    intent_info: IntentRoutingInfo, 
    warning_str: str
) -> ChatResponse:
    user_type = request.userType.strip().lower()
    message = request.message.strip()
    language = request.language.strip().lower()
    intent = intent_info.intent

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
                    answer = f"**{scheme['name']}** ke liye required documents yeh hain: {docs_str}"
                elif language == "hinglish":
                    answer = f"**{scheme['name']}** ke liye required documents list: {docs_str}"
                else:
                    answer = f"The documents required for **{scheme['name']}** are: {docs_str}"
                action_step = "Gather identity proof and land/business documentation."
                
            elif intent == "application_process":
                steps_str = " ".join(scheme["steps"])
                if language == "hi":
                    answer = f"**{scheme['name']}** ke liye offline ya online application steps: {steps_str}"
                elif language == "hinglish":
                    answer = f"**{scheme['name']}** ke liye application process details: {steps_str}"
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
                domain="government",
                actionable_next_step=action_step
            )

    # 4. government_service (e.g. pension)
    if intent == "government_service":
        if language == "hi":
            answer = "पेंशन और नागरिक उपयोगिताओं (government services/pension) के लिए कृपया अपने स्थानीय नगर पालिका या ग्राम पंचायत कार्यालय से संपर्क करें।"
        elif language == "hinglish":
            answer = "Pensions aur government services ke liye local administration ya nagar palika office visit karein."
        else:
            answer = "Pensions and civic utilities can be processed via local municipality or village panchayat offices."
        return ChatResponse(
            answer=answer,
            sources=[],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="government",
            actionable_next_step="Visit your nearest local government administration office."
        )

    # Default fallback government scheme query (PROBLEM-FIRST verification: "Mujhe scheme chahiye" vague checking)
    if language == "hi":
        answer = "सरकारी योजना सहायता के लिए कृपया आधिकारिक विवरणों की जांच करें और आवश्यक दस्तावेज एकत्र करें।"
    else:
        answer = "For government schemes, please check official details and gather relevant documents."
    return ChatResponse(
        answer=answer,
        sources=[],
        warning=warning_str,
        language=language,
        intent=intent,
        domain="government",
        actionable_next_step="Verify details with local authorities."
    )
