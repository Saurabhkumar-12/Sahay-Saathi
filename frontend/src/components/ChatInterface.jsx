import React, { useState, useEffect, useRef } from 'react';
import { Send, ArrowLeft, RefreshCw, AlertTriangle, BookOpen, MessageSquare, ShieldAlert, PhoneCall, ExternalLink } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const HELPLINES = [
  { name: "National Emergency Number", phone: "112", desc: "All emergencies across India" },
  { name: "Kisan Call Centre (Farmers)", phone: "1800-180-1551", desc: "Agricultural assistance" },
  { name: "National Women Helpline", phone: "1091", desc: "Women's safety & grievance" },
  { name: "Divyangjan (Disability) Help", phone: "1800-572-8980", desc: "Ministry of Social Justice" },
  { name: "Child Helpline", phone: "1098", desc: "Child care & protection" }
];

export default function ChatInterface({ userType, language, onBack }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'schemes' | 'safety'
  const [schemes, setSchemes] = useState([]);
  const messagesEndRef = useRef(null);

  // Suggested questions based on User Type
  const suggestedQuestions = {
    farmer: [
      { text: "PM Kisan ke liye kaun eligible hai?", label: "PM-Kisan Eligibility (Hinglish)" },
      { text: "Who is eligible for PM Kisan?", label: "PM-Kisan Eligibility (English)" },
      { text: "Mujhe farming ke liye government support chahiye.", label: "Farming Support Request" }
    ],
    "street vendor": [
      { text: "Mere liye government loan scheme kaun si hai?", label: "Loan Schemes (Hinglish)" },
      { text: "PM SVANidhi ke liye kya documents chahiye?", label: "SVANidhi Documents" }
    ],
    artisan: [
      { text: "Artisan ke liye government help kya hai?", label: "Artisan Benefits" },
      { text: "PM Vishwakarma registration kaise karein?", label: "Vishwakarma Guide" }
    ],
    fisherman: [
      { text: "Fisherman ke liye government support kya hai?", label: "Fisheries Support" }
    ],
    "rural worker": [
      { text: "MGNREGA job card kaise banta hai?", label: "MGNREGA Job Card" }
    ],
    "person with disability": [
      { text: "UDID card ke kya benefits hain?", label: "UDID Benefits" }
    ],
    citizen: [
      { text: "Accident insurance scheme kaunsi hai?", label: "Insurance Support" }
    ],
    other: [
      { text: "Mujhe scheme chahiye.", label: "Browse Schemes" }
    ]
  };

  const getSuggestions = () => {
    return suggestedQuestions[userType.toLowerCase()] || suggestedQuestions['other'];
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Load knowledge base schemes for reference
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health`)
      .then(() => {
        // Fetch matching schemes or use local copy of knowledge base
        // To be safe, we load from backend. Let's create an endpoint in backend later or just load from static database.
        // For now, we will fetch our local knowledge_base json if possible, or fallback to frontend hardcoded values.
        setSchemes([
          {
            name: "PM Kisan Samman Nidhi",
            description: "₹6,000 per year directly to small and marginal farmers.",
            target_users: ["farmer"],
            eligibility: "Small and marginal farmers owning land up to 2 hectares.",
            required_documents: ["Aadhaar Card", "Landholding papers", "Bank details"],
            application_steps: ["Visit pmkisan.gov.in portal", "Apply via 'New Farmer Registration'"],
            official_source: "https://pmkisan.gov.in/"
          },
          {
            name: "PM SVANidhi",
            description: "Collateral-free working capital loan up to ₹10,000 for street vendors.",
            target_users: ["street vendor"],
            eligibility: "Urban street vendors vending on or before March 24, 2020.",
            required_documents: ["Aadhaar Card", "Certificate of Vending (CoV)", "Bank details"],
            application_steps: ["Visit pmsvanidhi.mohua.gov.in", "OTP verification", "Submit details"],
            official_source: "https://pmsvanidhi.mohua.gov.in/"
          },
          {
            name: "PM Vishwakarma Scheme",
            description: "Toolkit incentive of ₹15,000 and low-interest loans for artisans.",
            target_users: ["artisan"],
            eligibility: "Traditional artisans in 18 trades (carpenter, potter, tailor etc.)",
            required_documents: ["Aadhaar Card", "Ration Card", "Bank Passbook"],
            application_steps: ["Register through CSC centers", "Biometric Aadhaar authentication"],
            official_source: "https://pmvishwakarma.gov.in/"
          }
        ]);
      })
      .catch((err) => {
        console.error("Backend offline: ", err);
      });
  }, []);

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;

    // Clear inputs and error
    if (!textToSend) setInputText('');
    setError(null);
    setLoading(true);

    // Add user message
    const userMessage = { sender: 'user', text };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          language: language,
          userType: userType
        }),
      });

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error("Rate limit exceeded. Please wait a minute before sending another message.");
        }
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to communicate with Sahay Saathi AI.");
      }

      const data = await response.json();
      
      // Add assistant response
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: data.answer,
        sources: data.sources,
        warning: data.warning,
        intent: data.intent,
        actionable_next_step: data.actionable_next_step
      }]);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  const getUserTypeEmoji = (type) => {
    switch (type.toLowerCase()) {
      case 'farmer': return '🌾';
      case 'street vendor': return '🛒';
      case 'artisan': return '🎨';
      case 'fisherman': return '🎣';
      case 'rural worker': return '👷';
      case 'person with disability': return '♿';
      case 'citizen': return '👤';
      default: return '💼';
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-h-[800px] w-full bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="bg-emerald-600 text-white p-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <button 
            onClick={onBack}
            className="p-1 hover:bg-emerald-700 rounded-lg transition-colors"
            title="Go Back"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h2 className="font-bold text-lg flex items-center gap-1.5">
              <span>Sahay Saathi AI</span>
              <span className="text-sm bg-emerald-700 px-2 py-0.5 rounded-full font-normal">
                {getUserTypeEmoji(userType)} {userType.toUpperCase()}
              </span>
            </h2>
            <p className="text-xs text-emerald-100 font-medium">
              Language: <span className="capitalize">{language}</span>
            </p>
          </div>
        </div>
        <div className="flex bg-emerald-700 rounded-lg p-0.5 text-sm">
          <button 
            onClick={() => setActiveTab('chat')}
            className={`px-3 py-1 rounded-md flex items-center gap-1.5 font-medium transition-all ${activeTab === 'chat' ? 'bg-white text-emerald-800' : 'text-white hover:bg-emerald-600'}`}
          >
            <MessageSquare className="w-4 h-4" />
            Chat
          </button>
          <button 
            onClick={() => setActiveTab('schemes')}
            className={`px-3 py-1 rounded-md flex items-center gap-1.5 font-medium transition-all ${activeTab === 'schemes' ? 'bg-white text-emerald-800' : 'text-white hover:bg-emerald-600'}`}
          >
            <BookOpen className="w-4 h-4" />
            Schemes
          </button>
          <button 
            onClick={() => setActiveTab('safety')}
            className={`px-3 py-1 rounded-md flex items-center gap-1.5 font-medium transition-all ${activeTab === 'safety' ? 'bg-white text-emerald-800' : 'text-white hover:bg-emerald-600'}`}
          >
            <PhoneCall className="w-4 h-4" />
            Help / Safety
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50">
        {activeTab === 'chat' && (
          <div className="flex flex-col h-full">
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
                <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center text-emerald-600 mb-4 border border-emerald-100">
                  {getUserTypeEmoji(userType) ? (
                    <span className="text-3xl">{getUserTypeEmoji(userType)}</span>
                  ) : (
                    <MessageSquare className="w-8 h-8" />
                  )}
                </div>
                <h3 className="font-semibold text-lg text-slate-800 mb-2">
                  Welcome to Sahay Saathi
                </h3>
                <p className="text-sm text-slate-500 max-w-sm mb-6">
                  Aap mujhe government schemes, eligibility, documents ya safety helpline ke baare mein kuch bhi pooch sakte hain.
                </p>

                {/* Suggestions */}
                <div className="w-full max-w-md">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 text-left">
                    Suggested Questions
                  </p>
                  <div className="flex flex-col gap-2">
                    {getSuggestions().map((s, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(s.text)}
                        className="w-full text-left p-3 bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 rounded-lg text-sm transition-all text-slate-700 font-medium shadow-sm hover:shadow"
                      >
                        {s.label}
                        <span className="block text-xs text-slate-400 font-normal mt-0.5">"{s.text}"</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((m, idx) => (
                  <div 
                    key={idx} 
                    className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div 
                      className={`max-w-[85%] rounded-lg p-3.5 shadow-sm text-sm ${
                        m.sender === 'user' 
                          ? 'bg-emerald-600 text-white rounded-br-none' 
                          : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'
                      }`}
                    >
                      {m.sender === 'assistant' && m.intent && (
                        <div className="mb-2">
                          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                            {m.intent.replace('_', ' ')}
                          </span>
                        </div>
                      )}
                      
                      <p className="whitespace-pre-line leading-relaxed">{m.text}</p>

                      {/* Matched Sources */}
                      {m.sources && m.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-100">
                          <p className="text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1">
                            <BookOpen className="w-3 h-3" /> Grounded Official Sources:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {m.sources.map((src, sIdx) => (
                              <a
                                key={sIdx}
                                href={src.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-emerald-700 text-xs px-2.5 py-1 rounded font-medium transition-colors"
                              >
                                {src.name}
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Verification Warnings */}
                      {m.warning && (
                        <div className="mt-2.5 bg-amber-50 border-l-4 border-amber-500 p-2.5 rounded text-xs text-amber-800 flex gap-2">
                          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                          <div>
                            <span className="font-semibold">Note:</span> {m.warning}
                          </div>
                        </div>
                      )}

                      {/* Actionable Next Step */}
                      {m.sender === 'assistant' && m.actionable_next_step && (
                        <div className="mt-2.5 bg-emerald-50 border-l-4 border-emerald-500 p-2.5 rounded text-xs text-emerald-800 flex gap-2">
                          <div className="font-bold flex-shrink-0">Next Action:</div>
                          <div>{m.actionable_next_step}</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex items-center gap-2 text-slate-500 text-sm mt-4">
                <RefreshCw className="w-4 h-4 animate-spin text-emerald-600" />
                <span>Sahay Saathi is thinking...</span>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-lg text-sm text-red-700 flex gap-2.5 mt-4">
                <ShieldAlert className="w-5 h-5 text-red-500 flex-shrink-0" />
                <div>
                  <span className="font-semibold">Error:</span> {error}
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Reference Schemes Tab */}
        {activeTab === 'schemes' && (
          <div className="space-y-4">
            <h3 className="font-bold text-slate-800 text-base mb-3 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-emerald-600" />
              Curated Schemes for {userType.toUpperCase()}s
            </h3>
            <div className="grid gap-4">
              {schemes
                .filter(s => s.target_users.includes(userType.toLowerCase()) || userType.toLowerCase() === 'citizen' || userType.toLowerCase() === 'other')
                .map((s, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-emerald-700 text-sm">{s.name}</h4>
                      <a 
                        href={s.official_source} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs font-semibold text-slate-400 hover:text-emerald-600 flex items-center gap-0.5"
                      >
                        Official Website <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <p className="text-xs text-slate-600 mb-3">{s.description}</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs border-t border-slate-100 pt-3">
                      <div>
                        <span className="font-semibold text-slate-500 block mb-0.5">Eligibility:</span>
                        <p className="text-slate-700">{s.eligibility}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-slate-500 block mb-0.5">Required Documents:</span>
                        <ul className="list-disc pl-4 text-slate-700 space-y-0.5">
                          {s.required_documents.map((d, dIdx) => <li key={dIdx}>{d}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>
              ))}
            </div>
          </div>
        )}

        {/* Helplines and Safety Tab */}
        {activeTab === 'safety' && (
          <div className="space-y-4">
            <h3 className="font-bold text-slate-800 text-base mb-3 flex items-center gap-2">
              <PhoneCall className="w-5 h-5 text-emerald-600" />
              Official Government Helplines
            </h3>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3.5 text-xs text-amber-800 mb-4 flex gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
              <p>
                <strong>Warning:</strong> Use these contact numbers only for genuine queries and help. These are verified official contacts from Indian government directories.
              </p>
            </div>
            <div className="grid gap-3">
              {HELPLINES.map((h, idx) => (
                <div key={idx} className="bg-white border border-slate-200 rounded-lg p-3 flex justify-between items-center shadow-sm">
                  <div>
                    <h4 className="font-bold text-slate-800 text-sm">{h.name}</h4>
                    <p className="text-xs text-slate-500">{h.desc}</p>
                  </div>
                  <a
                    href={`tel:${h.phone}`}
                    className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 font-bold px-3 py-1.5 rounded-lg text-sm flex items-center gap-1 transition-all"
                  >
                    <PhoneCall className="w-4 h-4" />
                    {h.phone}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      {activeTab === 'chat' && (
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
          className="border-t border-slate-200 p-3 bg-white flex gap-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading}
            placeholder="Type your question here (Hindi, Hinglish, or English)..."
            className="flex-1 border border-slate-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-emerald-500 disabled:bg-slate-50 disabled:text-slate-400"
          />
          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white rounded-lg p-2.5 transition-colors flex items-center justify-center flex-shrink-0 shadow-sm"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      )}
    </div>
  );
}
