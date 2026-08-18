# Sahay Saathi Development Blueprint

**Sahay Saathi** is an AI-powered citizen assistance platform designed for underserved communities in India (Problem Statement 5 — AI for Public Good). It assists users in understanding government schemes, eligibility criteria, application procedures, and livelihood/safety information in simple terms, supporting English, Hindi, and Hinglish.

This plan details the MVP scaffolding, layout, architecture, and technology implementation.

## User Review Required

> [!IMPORTANT]
> This plan replaces the previous misunderstanding. The target application is now defined as a responsive web-first application using React+Vite for the frontend, Python+FastAPI for the backend, and Gemini API for natural language assistance grounded in official source data.

## Open Questions

None. The project scope, technical stack, core screens, and test scenarios are fully defined by the official project definition.

## Proposed Changes

### Configuration and Documentation

We will establish the repository structure, documentation, configuration templates, and repository rules.

#### [NEW] [README.md](file:///e:/Sahay Saathi/README.md)
Contains the project overview, setup commands, and technical framework details.

#### [NEW] [architecture.md](file:///e:/Sahay Saathi/architecture.md)
Outlines the system architecture, API endpoints (`/api/health`, `/api/chat`), security measures, data grounding strategy, and LLM prompting guidelines.

#### [NEW] [implementation_plan.md](file:///e:/Sahay Saathi/implementation_plan.md)
The version-controlled copy of this implementation plan inside the workspace root.

#### [NEW] [.gitignore](file:///e:/Sahay Saathi/.gitignore)
Rules to prevent committing `.env`, dependencies, build output, and credential secrets.

#### [NEW] [.env.example](file:///e:/Sahay Saathi/.env.example)
Example environment variables for port configurations, rate limits, and Gemini API Key placeholders.

---

### Backend Scaffolding

Set up a simple FastAPI REST API with input validation, rate limiting, and Gemini grounding.

#### [NEW] [backend/requirements.txt](file:///e:/Sahay Saathi/backend/requirements.txt)
FastAPI, Uvicorn, Pydantic, Slowapi (rate limiting), Google GenAI SDK, and pytest.

#### [NEW] [backend/app/main.py](file:///e:/Sahay Saathi/backend/app/main.py)
FastAPI app containing health check and chat endpoints, CORS settings, error handlers, and rate limiter.

#### [NEW] [backend/app/schemas.py](file:///e:/Sahay Saathi/backend/app/schemas.py)
Pydantic schemas for strict request/response validation (chat request, response parameters).

#### [NEW] [backend/app/services/gemini.py](file:///e:/Sahay Saathi/backend/app/services/gemini.py)
Gemini client wrapper with system instructions enforcing grounding, simple language, and context-dependent personas (Farmer, Street Vendor, etc.).

#### [NEW] [backend/data/knowledge_base.json](file:///e:/Sahay Saathi/backend/data/knowledge_base.json)
A curated database of official government schemes (PM-Kisan, PM SVANidhi, PM Vishwakarma, etc.) for source-grounding the LLM.

---

### Frontend Scaffolding

Set up a responsive React + Vite application.

#### [NEW] [frontend/package.json](file:///e:/Sahay Saathi/frontend/package.json)
React, React DOM, Tailwind CSS (for accessible, responsive styling), and Lucide React (icons).

#### [NEW] [frontend/src/App.jsx](file:///e:/Sahay Saathi/frontend/src/App.jsx)
Main component orchestrating flow transitions: Home → Select User Type → Language Selection → AI Chat Interface.

#### [NEW] [frontend/src/components/ChatInterface.jsx](file:///e:/Sahay Saathi/frontend/src/components/ChatInterface.jsx)
Accessible chat view rendering user/assistant messages, sources, alerts, warnings, and loading indicators.

## Verification Plan

### Automated Tests

We will run backend integration tests to check schema validation, rate limiting, and response format.
```bash
pytest backend/tests/
```

### Manual Verification

We will manually test the following chat inputs using the `/api/chat` API or the UI:
1. **Hindi/Hinglish Query (Farmer Context):** `"PM Kisan ke liye kaun eligible hai?"`
2. **English Query (Farmer Context):** `"Who is eligible for PM Kisan?"`
3. **Street Vendor Context:** `"Mere liye government loan scheme kaun si hai?"`
4. **Artisan Context:** `"Artisan ke liye government help kya hai?"`
5. **Safety Query:** `"Mujhe safety ke liye help chahiye."`
6. **Ambiguous Query:** `"Mujhe scheme chahiye."` (Expect the AI to ask clarifying questions about user category).
7. **Out-of-scope Query:** `"Tomorrow stock market mein kya hoga?"` (Expect the AI to decline answering).
8. **Rate Limiting:** Send more than the allowed requests within the window to verify `429 Too Many Requests`.
