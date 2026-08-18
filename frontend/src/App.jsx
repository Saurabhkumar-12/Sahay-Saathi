import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import { HelpCircle, ChevronRight, Globe, Languages, ArrowLeft } from 'lucide-react';

const USER_TYPES = [
  { id: 'farmer', name: 'Farmer', emoji: '🌾', description: 'Kheti-kisani support, PM Kisan scheme, and fertilizers.' },
  { id: 'street vendor', name: 'Street Vendor', emoji: '🛒', description: 'Working capital loans, PM SVANidhi registry.' },
  { id: 'artisan', name: 'Artisan', emoji: '🎨', description: 'Traditional crafts support, Vishwakarma tools & aid.' },
  { id: 'fisherman', name: 'Fisherman', emoji: '🎣', description: 'Fisheries sector development, boat subsidies, Blue Revolution.' },
  { id: 'rural worker', name: 'Rural Worker', emoji: '👷', description: 'MGNREGA job cards, wage guidelines, rural work demand.' },
  { id: 'person with disability', name: 'Person with Disability', emoji: '♿', description: 'UDID cards, travel concessions, disability pension.' },
  { id: 'citizen', name: 'Citizen', emoji: '👤', description: 'General government insurance, public services support.' },
  { id: 'other', name: 'Other / Dusra', emoji: '💼', description: 'General queries and local assistance information.' }
];

const LANGUAGES = [
  { id: 'en', label: 'English', sub: 'Simple English explanations' },
  { id: 'hi', label: 'Hindi (हिंदी)', sub: 'सरल हिंदी स्पष्टीकरण (देवनागरी)' },
  { id: 'hinglish', label: 'Hinglish', sub: 'Roman script Hindi (e.g., "Aap eligible hain")' }
];

export default function App() {
  const [step, setStep] = useState('home'); // 'home' | 'userType' | 'language' | 'chat'
  const [selectedUserType, setSelectedUserType] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');

  const startFlow = () => setStep('userType');
  const selectUserType = (typeId) => {
    setSelectedUserType(typeId);
    setStep('language');
  };
  const selectLanguage = (langId) => {
    setSelectedLanguage(langId);
    setStep('chat');
  };

  const handleBack = () => {
    if (step === 'userType') setStep('home');
    else if (step === 'language') setStep('userType');
    else if (step === 'chat') setStep('language');
  };

  const resetAll = () => {
    setSelectedUserType('');
    setSelectedLanguage('');
    setStep('home');
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-4">
      {/* App Container */}
      <div className="w-full max-w-4xl flex flex-col items-center">
        
        {/* Top Navbar */}
        <header className="w-full flex items-center justify-between py-4 mb-6 border-b border-slate-200">
          <div className="flex items-center gap-2 cursor-pointer" onClick={resetAll}>
            <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white font-bold text-xl shadow-md">
              SS
            </div>
            <div>
              <h1 className="font-extrabold text-xl text-slate-800 tracking-tight">Sahay Saathi</h1>
              <p className="text-xs text-slate-500 font-medium">AI-powered Citizen Assistance</p>
            </div>
          </div>
          <div className="flex items-center gap-1 bg-white border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600">
            <Globe className="w-4 h-4 text-slate-400" />
            <span>Digital India Hackathon</span>
          </div>
        </header>

        {/* Dynamic Screen Steps */}
        {step === 'home' && (
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center mt-6">
            <span className="text-5xl mb-4 inline-block">🇮🇳</span>
            <h2 className="font-black text-3xl text-slate-800 tracking-tight mb-2">Sahay Saathi</h2>
            <p className="text-emerald-600 font-bold text-sm tracking-wide uppercase mb-4">
              AI-powered citizen assistance platform
            </p>
            <p className="text-slate-500 text-base leading-relaxed mb-8">
              Get simple information about government schemes, services, and assistance in your local language. Grounded in official sources.
            </p>
            <button
              onClick={startFlow}
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all text-base flex items-center justify-center gap-2"
            >
              Get Started / शुरू करें
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {step === 'userType' && (
          <div className="w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-6 md:p-8">
            <div className="flex items-center justify-between mb-6">
              <button 
                onClick={handleBack}
                className="flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest bg-emerald-50 px-2.5 py-1 rounded-full">
                Step 1 of 2
              </span>
            </div>
            
            <h2 className="font-black text-2xl text-slate-800 mb-2">Aap kya kaam karte hain?</h2>
            <p className="text-slate-500 text-sm mb-6">Select your category to help the AI understand your profile context.</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {USER_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => selectUserType(type.id)}
                  className="flex items-start text-left p-4 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/30 transition-all shadow-sm hover:shadow"
                >
                  <span className="text-3xl mr-4 flex-shrink-0 mt-0.5">{type.emoji}</span>
                  <div>
                    <h3 className="font-bold text-slate-800 text-base mb-1">{type.name}</h3>
                    <p className="text-xs text-slate-500 leading-normal">{type.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 'language' && (
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-lg border border-slate-200 p-6 md:p-8">
            <div className="flex items-center justify-between mb-6">
              <button 
                onClick={handleBack}
                className="flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest bg-emerald-50 px-2.5 py-1 rounded-full">
                Step 2 of 2
              </span>
            </div>

            <h2 className="font-black text-2xl text-slate-800 mb-2 flex items-center gap-2">
              <Languages className="w-6 h-6 text-emerald-600" />
              Select Language
            </h2>
            <p className="text-slate-500 text-sm mb-6">Aap kis bhasha mein baat karna chahte hain?</p>

            <div className="space-y-3">
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.id}
                  onClick={() => selectLanguage(lang.id)}
                  className="w-full flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/30 text-left transition-all shadow-sm hover:shadow"
                >
                  <div>
                    <h3 className="font-bold text-slate-800 text-base">{lang.label}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{lang.sub}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-400" />
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 'chat' && (
          <ChatInterface 
            userType={selectedUserType} 
            language={selectedLanguage} 
            onBack={handleBack} 
          />
        )}

        {/* Footer */}
        <footer className="mt-8 text-center text-xs text-slate-400">
          <p>© 2026 Sahay Saathi. Dedicated to AI for Public Good & Inclusive Social Impact.</p>
          <p className="mt-1">All scheme information matches official sources on best-effort validation.</p>
        </footer>

      </div>
    </div>
  );
}
