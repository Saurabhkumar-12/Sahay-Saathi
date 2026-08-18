# Architecture & Data Flow

This document details the high-level architecture, flow, API design, and safety/grounding strategies for **Sahay Saathi**.

## System Overview

```text
       ┌────────────────────────┐
       │   React + Vite App     │ (Frontend)
       └───────────┬────────────┘
                   │
                   │ HTTP POST /api/chat
                   ▼
       ┌────────────────────────┐
       │   FastAPI Server       │ (Backend)
       │                        │
       │  ├─ Validation         │
       │  ├─ Rate Limiting      │
       │  └─ Session Handlers   │
       └─────┬────────────┬─────┘
             │            │
             │ Query      │ RAG Grounding Prompt
             ▼            ▼
   ┌──────────────┐  ┌──────────────┐
   │ Knowledge    │  │ Gemini API   │ (External)
   │ Base JSON    │  │ (API Key)    │
   └──────────────┘  └──────────────┘
```

## API Specifications

### 1. Health Check
- **Endpoint:** `GET /api/health`
- **Response:**
  ```json
  {
    "status": "healthy"
  }
  ```

### 2. Chat Endpoint
- **Endpoint:** `POST /api/chat`
- **Request Headers:**
  - `Content-Type: application/json`
  - Client IP (for rate limiting)
- **Request Body (JSON):**
  ```json
  {
    "message": "PM Kisan ke liye kaun eligible hai?",
    "language": "hi",
    "userType": "farmer"
  }
  ```
- **Response Body (JSON):**
  ```json
  {
    "answer": "PM Kisan Samman Nidhi ke under, chote aur marginal farmers eligible hain jinke paas cultivable land hai. Isme saal ka ₹6,000 milta hai.",
    "sources": [
      {
        "name": "PM-Kisan Samman Nidhi",
        "url": "https://pmkisan.gov.in/",
        "last_verified": "2026-08-01"
      }
    ],
    "warning": "Kripya dhyan dein: Yeh information educational purpose ke liye hai. Official application process ke liye official website par check karein.",
    "language": "hi"
  }
  ```

## AI Grounding and Behavior

To eliminate hallucinations regarding government rules and URLs, we implement **source-grounded response generation**:
1. **Local Search:** For every query, the backend retrieves matching schemes from the `knowledge_base.json` database.
2. **Context Enrichment:** The matched scheme records (along with user type and target language) are injected into the LLM prompt.
3. **Strict Constraints:**
   - The LLM is instructed *only* to explain the retrieved source data.
   - If no source records match or are relevant, the LLM must output: `"I could not verify this information from a reliable official source. Please check with the relevant government department."`
   - It is prohibited from fabricating eligibility guidelines, deadlines, or websites.

## Security Architecture

1. **Secret Isolation:** The `GEMINI_API_KEY` is maintained strictly backend-side. The client has no visibility.
2. **Input Validation:** Strict Pydantic models validate constraints (e.g., maximum string lengths, allowed language enums, allowed user types).
3. **Rate Limiting:** IP-based rate limiting prevents resource exhaustion.
4. **Error Shielding:** Internal server errors (e.g., tracebacks) are captured by global FastAPI handlers and masked with clean user-facing error messages while logs capture detailed error info.
