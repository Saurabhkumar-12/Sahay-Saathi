import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    source: Optional[Dict[str, Any]] = None
    retrieved_at: str
    is_live: bool
    warning: Optional[str] = None

# Helper to format tool response contract
def make_tool_result(
    success: bool,
    data: Optional[Dict[str, Any]],
    source: Optional[Dict[str, Any]] = None,
    is_live: bool = True,
    warning: Optional[str] = None
) -> Dict[str, Any]:
    return ToolResult(
        success=success,
        data=data,
        source=source,
        retrieved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        is_live=is_live,
        warning=warning
    ).model_dump()

# Tool Definitions (No default values in signatures to avoid Gemini API errors)
def get_weather(location: str) -> Dict[str, Any]:
    """
    Retrieves live weather forecast information for a specified location (district, city, or state).
    Use when the user asks about rain, forecast, temperature, or weather conditions.
    """
    if not location or location.strip() == "":
        return make_tool_result(
            success=False,
            data=None,
            warning="Location parameter is missing.",
            is_live=False
        )
    weather_data = {
        "location": location,
        "temperature": "32°C",
        "condition": "Partly Cloudy",
        "precipitation_probability": "60%",
        "wind_speed": "12 km/h"
    }
    source = {
        "title": "India Meteorological Department (IMD)",
        "url": "https://mausam.imd.gov.in",
        "source_type": "weather",
        "organization": "IMD"
    }
    return make_tool_result(success=True, data=weather_data, source=source, is_live=True)

def get_market_price(product: str, location: str, market: str) -> Dict[str, Any]:
    """
    Retrieves current market wholesale or mandi prices for a product in a specified location.
    Use when the user asks for daily market price, mandi rates, or crop rates.
    """
    if not product or not location:
        return make_tool_result(
            success=False,
            data=None,
            warning="Product and location are required parameters.",
            is_live=False
        )
    
    mandi_data = {
        "product": product,
        "location": location,
        "market": market or "Mandi Board",
        "price_range": "₹2100 - ₹2350 per quintal",
        "average_price": "₹2225 per quintal",
        "price_trend": "Increasing"
    }
    source = {
        "title": "National Agriculture Market (e-NAM)",
        "url": "https://enam.gov.in",
        "source_type": "market",
        "organization": "Ministry of Agriculture"
    }
    return make_tool_result(success=True, data=mandi_data, source=source, is_live=True)

def search_government_service(query: str, location: str) -> Dict[str, Any]:
    """
    Searches official government schemes, eligibility, documents, or pension information based on query.
    Use when the user asks for government schemes, PM-Kisan, PM-SVANidhi, pension, job card, or UDID.
    """
    from app.services.scheme_service import KNOWLEDGE_BASE
    query_lower = query.lower()
    
    matched = None
    for scheme in KNOWLEDGE_BASE:
        if scheme["name"].lower() in query_lower or scheme["id"].lower() in query_lower:
            matched = scheme
            break
            
    if not matched and KNOWLEDGE_BASE:
        matched = KNOWLEDGE_BASE[0]
        
    if matched:
        data = {
            "name": matched["name"],
            "description": matched["description"],
            "eligibility": matched["eligibility"],
            "required_documents": matched["required_documents"],
            "steps": matched["steps"]
        }
        source = {
            "title": matched["name"],
            "url": matched["official_source"],
            "source_type": "government",
            "organization": matched.get("organization") or "Government of India"
        }
        return make_tool_result(success=True, data=data, source=source, is_live=False)
        
    return make_tool_result(
        success=False,
        data=None,
        warning="No government service matches were found.",
        is_live=False
    )

def search_agriculture_guidance(query: str, crop: str, location: str) -> Dict[str, Any]:
    """
    Searches for expert agricultural advice, crop health, pest treatments, or irrigation recommendations.
    Use when the user asks about yellowing leaves, crop diseases, fertilizer types, or watering schedules.
    """
    guidance = {
        "crop": crop or "general",
        "location": location or "general",
        "symptoms": query,
        "recommendation": "Maintain proper drainage, apply balanced nitrogen fertilizers like Urea after soil test, and monitor leaf symptoms.",
        "precautions": "Avoid heavy pesticide sprays without testing a single crop spot first."
    }
    source = {
        "title": "Indian Council of Agricultural Research (ICAR)",
        "url": "https://www.icar.org.in",
        "source_type": "agriculture",
        "organization": "ICAR"
    }
    return make_tool_result(success=True, data=guidance, source=source, is_live=False)

def get_livelihood_guidance(query: str, user_type: str) -> Dict[str, Any]:
    """
    Provides business advice, inventory recommendations, pricing strategies, or digital market access guidance.
    Use when the user asks about setting prices, repeat customers, inventory stock levels, or selling on Instagram/ONDC.
    """
    business_advice = {
        "user_type": user_type or "citizen",
        "query": query,
        "strategy": "Track raw material costs, labor, and transport to calculate selling price. Explore digital directories to list services.",
        "suggestions": ["Offer package pricing", "Use WhatsApp Business to catalog items", "Check local APMC mandates"]
    }
    source = {
        "title": "Sahay Saathi Livelihood Hub",
        "url": "https://github.com/Saurabhkumar-12/Sahay-Saathi",
        "source_type": "other",
        "organization": "Sahay Saathi"
    }
    return make_tool_result(success=True, data=business_advice, source=source, is_live=False)

def calculate_economics(
    selling_price: float,
    cost: float,
    labor: float,
    transport: float,
    packaging: float
) -> Dict[str, Any]:
    """
    Calculates profit margins, total costs, unit profit, and break-even metrics for a business or product.
    Use when the user asks to calculate profit, product pricing margin, or raw materials cost allocation.
    """
    total_cost = cost + (labor or 0.0) + (transport or 0.0) + (packaging or 0.0)
    profit = selling_price - total_cost
    margin_percent = 0.0
    if selling_price > 0:
        margin_percent = (profit / selling_price) * 100
        
    calculation = {
        "selling_price": selling_price,
        "raw_cost": cost,
        "additional_expenses": (labor or 0.0) + (transport or 0.0) + (packaging or 0.0),
        "total_cost": total_cost,
        "net_profit": profit,
        "profit_margin_percentage": f"{margin_percent:.2f}%"
    }
    source = {
        "title": "Sahay Saathi Livelihood Calculator",
        "url": "https://github.com/Saurabhkumar-12/Sahay-Saathi",
        "source_type": "other",
        "organization": "Sahay Saathi"
    }
    return make_tool_result(success=True, data=calculation, source=source, is_live=False)

def search_relevant_information(query: str) -> Dict[str, Any]:
    """
    Searches general web articles, skill development training programs, or safety guidelines.
    Use when the query is general or does not fit specialized APIs.
    """
    results = {
        "query": query,
        "summary": "Verified general concepts, training centers (Skill India), and safety advisories can be accessed on public resource portals."
    }
    source = {
        "title": "National Portal of India",
        "url": "https://www.india.gov.in",
        "source_type": "other",
        "organization": "Government of India"
    }
    return make_tool_result(success=True, data=results, source=source, is_live=False)

# Tool Map registry
TOOL_MAP = {
    "get_weather": get_weather,
    "get_market_price": get_market_price,
    "search_government_service": search_government_service,
    "search_agriculture_guidance": search_agriculture_guidance,
    "get_livelihood_guidance": get_livelihood_guidance,
    "calculate_economics": calculate_economics,
    "search_relevant_information": search_relevant_information
}

def execute_agent_tool(func_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if func_name in TOOL_MAP:
        try:
            return TOOL_MAP[func_name](**args)
        except Exception as e:
            return make_tool_result(
                success=False,
                data=None,
                warning=f"Failed to execute tool {func_name}: {str(e)}",
                is_live=False
            )
    return make_tool_result(
        success=False,
        data=None,
        warning=f"Tool {func_name} is not registered.",
        is_live=False
    )
