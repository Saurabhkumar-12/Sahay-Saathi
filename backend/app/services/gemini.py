import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.schemas import ChatRequest, ChatResponse, GenericSource, IntentRoutingInfo
from app.services.router import route_intent
from app.services.scheme_service import match_schemes
from app.services.source_router import detect_language
from app.services.tool_router import (
    get_weather,
    get_market_price,
    search_government_service,
    search_agriculture_guidance,
    get_livelihood_guidance,
    calculate_economics,
    search_relevant_information,
    execute_agent_tool
)

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return None
    return genai.Client(api_key=api_key)

async def generate_assistance(request: ChatRequest) -> ChatResponse:
    user_type = request.userType.strip().lower()
    message = request.message.strip()
    language = detect_language(message, request.language.strip().lower())
    
    # 1. Route Intent & Domain for routing metadata
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
Your goal is to understand the user's problem first, then select the appropriate tool or reasoning mechanism to help them.

CONTEXT:
User Type: {user_type}
Preferred Language: {language}
Classified Intent: {routing_info.intent}
Classified Domain: {routing_info.domain}

SCHEME REFERENCE DATA:
{schemes_context}

RULES:
1. Adaptive Problem-First Routing: Analyze the user's real problem. If you need external data (weather forecasts, real-time market prices, safety advisories, or official government criteria), select the appropriate tool.
2. Factual Grounding:
   - Use the tool result to form your answer.
   - Do not invent weather, prices, sea safety states, or official criteria that are absent from tool responses.
   - Do not force government schemes on non-government queries.
3. Crop Health and Agricultural Cautious Phrasing:
   - For crop health problems (e.g. yellow leaves), explain that symptoms can have multiple causes.
   - Use cautious phrasing ("Possible causes include...", not "Your crop has...").
   - Ask important diagnostic questions (crop age, location, leaf location, irrigation, recent fertilizer) to help them check.
   - Recommend KVK/agricultural extension experts for serious issues.
4. If live data could not be verified by the weather/market/safety tools, explicitly state that in the answer.
5. Translate or summarize the tool results into the user's target language/style (Hindi, English, or Hinglish) to maintain language consistency.
6. Make sure the final response is formatted in JSON matching the ChatResponse schema.
"""

    tools_list = [
        get_weather,
        get_market_price,
        search_government_service,
        search_agriculture_guidance,
        get_livelihood_guidance,
        calculate_economics,
        search_relevant_information
    ]

    try:
        # Call model to see if it wants to invoke a tool
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools_list,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                temperature=0.1
            )
        )
        
        # If the model wants to call a tool:
        if response.function_calls:
            # Build conversation history
            history = [
                types.Content(role="user", parts=[types.Part.from_text(text=message)]),
                response.candidates[0].content
            ]
            
            # Execute all requested functions
            for call in response.function_calls:
                result = execute_agent_tool(call.name, call.args)
                history.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=call.name,
                                response=result
                            )
                        ]
                    )
                )
                
            # Call Gemini again to get structured JSON response grounded in tool results
            final_response = client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
                contents=history,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ChatResponse,
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            response_data = json.loads(final_response.text)
            return ChatResponse(**response_data)
            
        else:
            # No tool call was requested; ask Gemini to generate JSON response directly
            direct_response = client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
                contents=message,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ChatResponse,
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            response_data = json.loads(direct_response.text)
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
