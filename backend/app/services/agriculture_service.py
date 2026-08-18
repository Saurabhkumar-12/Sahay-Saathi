from typing import Dict, Any, List
from app.schemas import ChatResponse, SchemeSource

def handle_agriculture_mock(
    message: str, 
    user_type: str, 
    language: str, 
    intent: str, 
    warning_str: str
) -> ChatResponse:
    msg_lower = message.lower()
    
    # 1. crop_health intent mock
    if intent == "crop_health":
        if language == "hi":
            answer = (
                "फसल में पत्तों का पीला होना (yellowing of leaves) कई कारणों से हो सकता है।\n"
                "संभावित कारणों में शामिल हैं:\n"
                "- नाइट्रोजन (Nitrogen) या अन्य पोषक तत्वों की कमी\n"
                "- अधिक सिंचाई (overwatering) या जलभराव\n"
                "- कीटों का हमला या फंगल इन्फेक्शन (जैसे पीला रतुआ/rust fungus)\n\n"
                "सुरक्षित तत्काल सावधानियां:\n"
                "- जब तक सही कारण स्पष्ट न हो, अतिरिक्त यूरिया या उर्वरक का छिड़काव न करें।\n"
                "- खेत में पानी जमा न होने दें और जल निकासी (drainage) सुनिश्चित करें।\n\n"
                "कृपया हमें यह जानकारी दें:\n"
                "1. आपकी गेहूं की फसल कितने दिनों की (crop age) है?\n"
                "2. आपका जिला/राज्य (location) कौन सा है?\n"
                "3. पीले पत्ते नीचे के हैं या ऊपर के?\n"
                "4. सिंचाई (irrigation) की क्या स्थिति है?\n"
                "5. हाल ही में कौन सी खाद/उर्वरक डाली गई है?\n\n"
                "यदि समस्या गंभीर है, तो कृपया अपने नजदीकी कृषि विज्ञान केंद्र (KVK) या स्थानीय कृषि विस्तार अधिकारी से संपर्क करें।"
            )
            action_step = "फसल की आयु, स्थान और पत्तों का विवरण साझा करें या स्थानीय कृषि अधिकारी से परामर्श लें।"
        elif language == "hinglish":
            answer = (
                "Wheat crop ke leaves ka yellow hona multiple factors ki wajah se ho sakta hai.\n"
                "Possible causes include:\n"
                "- Nitrogen ya other nutrients ki kami (deficiency)\n"
                "- Overwatering ya bad drainage condition\n"
                "- Pest attack ya fungal rust infection\n\n"
                "Safe immediate precautions:\n"
                "- Jab tak clear diagnosis na ho, excess fertilizer ya chemical spray na karein.\n"
                "- Water drainage check karein taaki root rot na ho.\n\n"
                "Important questions to check:\n"
                "1. Crop age kya hai (wheat kitne din ka hai)?\n"
                "2. Location / area kya hai?\n"
                "3. Upper leaves yellow hain ya lower leaves?\n"
                "4. Irrigation timeline aur frequency kya hai?\n"
                "5. Recently kaun sa fertilizer apply kiya hai?\n\n"
                "Serious cases ke liye local Krishi Vigyan Kendra (KVK) or Block Agriculture Officer se consult karein."
            )
            action_step = "Crop age and yellowing details tell karein ya local KVK expert se consult karein."
        else:
            answer = (
                "Yellowing of wheat leaves can have multiple possible causes.\n"
                "Possible causes include:\n"
                "- Nutrient deficiency (especially Nitrogen)\n"
                "- Overwatering or poor soil drainage\n"
                "- Fungal diseases (such as yellow rust) or insect infestation\n\n"
                "Safe immediate precautions:\n"
                "- Avoid applying excessive fertilizers or chemicals until the specific cause is confirmed.\n"
                "- Ensure proper water drainage from the field.\n\n"
                "To help diagnose, please share:\n"
                "1. What is the crop age (in days)?\n"
                "2. What is your location/region?\n"
                "3. Are the lower or upper leaves turning yellow?\n"
                "4. What is the current irrigation condition?\n"
                "5. Did you apply any fertilizer recently?\n\n"
                "We recommend consulting a local agricultural extension center (KVK) or agricultural expert for serious issues."
            )
            action_step = "Provide crop age, location, and leaf detail, or consult local agricultural office."
            
        return ChatResponse(
            answer=answer,
            sources=[],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="agriculture",
            actionable_next_step=action_step
        )
        
    # 2. irrigation intent mock
    elif intent == "irrigation":
        if language == "hi":
            answer = (
                "आपके खेत में पानी की कमी (water shortage) को दूर करने के लिए निम्नलिखित उपाय उपयोगी हो सकते हैं:\n"
                "- पानी बचाने के लिए ड्रिप सिंचाई (drip irrigation) या स्प्रिंकलर सिस्टम अपनाएं।\n"
                "- स्थानीय सिंचाई विभाग या ब्लॉक अधिकारी से सरकारी पंपसेट या बोरवेल योजनाओं के बारे में संपर्क करें।\n"
                "- मृदा नमी (soil moisture) बनाए रखने के लिए गीली घास (mulching) का उपयोग करें।"
            )
            action_step = "स्थानीय ब्लॉक कृषि या सिंचाई विभाग कार्यालय से संपर्क करें।"
        elif language == "hinglish":
            answer = (
                "Aapke khet mein water shortage door karne ke liye standard tips:\n"
                "- Drip irrigation ya sprinkler systems se water conserve karein.\n"
                "- Local irrigation/block officer se tubewell aur solar pump subsidy ke baare mein jaanein.\n"
                "- Soil moisture retain karne ke liye mulching technique try karein."
            )
            action_step = "Block agriculture officer ya local irrigation office visit karein."
        else:
            answer = (
                "Tips to manage water shortage in your agricultural field:\n"
                "- Adopt drip or sprinkler irrigation systems to conserve water resources.\n"
                "- Inquire with block officials regarding solar water pump subsidies and borewell schemes.\n"
                "- Implement mulching to retain soil moisture and prevent evaporation."
            )
            action_step = "Contact your local block agriculture or irrigation officer."
            
        return ChatResponse(
            answer=answer,
            sources=[],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="agriculture",
            actionable_next_step=action_step
        )
        
    # 3. market_price intent mock
    elif intent == "market_price":
        # Cautious mock response to prevent hallucinating prices
        if language == "hi":
            answer = (
                "हम वास्तविक समय (live) के बाजार भाव बिना पुष्टि के साझा नहीं कर सकते।\n"
                "कृपया आज के सही थोक भाव जानने के लिए सरकार के आधिकारिक ई-नाम (e-NAM) पोर्टल पर जाएं या अपने नजदीकी मंडी बोर्ड (APMC) से संपर्क करें।"
            )
            action_step = "आज का भाव जांचने के लिए आधिकारिक e-NAM पोर्टल पर जाएं।"
        elif language == "hinglish":
            answer = (
                "Hum bina verification ke live market prices share nahi kar sakte.\n"
                "Please wholesale rates verify karne ke liye government ke official e-NAM portal par check karein ya local APMC mandi visit karein."
            )
            action_step = "e-NAM official portal par rates check karein."
        else:
            answer = (
                "We cannot provide unverified real-time market prices to avoid misinformation.\n"
                "Please refer to the official e-NAM (National Agriculture Market) portal or contact your local APMC mandi office for accurate daily rates."
            )
            action_step = "Check official e-NAM portal for today's market prices."
            
        return ChatResponse(
            answer=answer,
            sources=[],
            warning=warning_str,
            language=language,
            intent=intent,
            domain="agriculture",
            actionable_next_step=action_step
        )
        
    # Fallback to general agriculture
    if language == "hi":
        answer = "खेती से जुड़े विभिन्न सवालों के समाधान के लिए कृपया कृषि विज्ञान केंद्र से संपर्क करें।"
        action_step = "कृषि केंद्र से संपर्क करें।"
    elif language == "hinglish":
        answer = "Farming se related problems ke local support ke liye Agriculture Office contact karein."
        action_step = "Agriculture extension center contact karein."
    else:
        answer = "For agriculture-related issues, please contact your local Krishi Vigyan Kendra or extension officer."
        action_step = "Contact agriculture extension office."
        
    return ChatResponse(
        answer=answer,
        sources=[],
        warning=warning_str,
        language=language,
        intent=intent,
        domain="agriculture",
        actionable_next_step=action_step
    )
