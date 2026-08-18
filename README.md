# Sahay Saathi

**AI-powered citizen assistance platform for underserved communities in India.**

Sahay Saathi is a responsive web application designed to help citizens, particularly those in underserved communities (farmers, street vendors, artisans, fishermen, rural workers, and people with disabilities), understand government schemes, eligibility criteria, required documents, application procedures, and general safety/livelihood information in simple language.

The platform supports natural language queries in English, Hindi, and Hinglish.

## Key Features

- **Contextual AI Assistance:** Adapts explanations to specific user categories (e.g., Farmer vs. Street Vendor).
- **Multilingual Support:** Accepts queries in Hindi, Hinglish, and English, explaining in clear, accessible terms.
- **Source-Grounded Responses:** Cross-references queries with a curated database of official government schemes to prevent hallucinating eligibility or contact info.
- **Security First:** Strict schema validation, API rate limiting, and server-side secret management.

## Project Structure

```text
Sahay-Saathi/
│
├── frontend/             # React + Vite + Tailwind CSS UI
│
├── backend/              # Python + FastAPI REST API
│   ├── app/              # API implementation and services
│   ├── data/             # Curated schemes & services knowledge base
│   └── tests/            # Test suite for validation, rate limiting, and API
│
├── README.md             # This file
├── architecture.md       # High-level architecture and system flow
├── implementation_plan.md# Detailed implementation blueprint
├── .gitignore            # Git exclusion rules
└── .env.example          # Environment variable template
```

## Setup Instructions

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Copy `.env.example` to `.env` in the backend root directory and add your `GEMINI_API_KEY`.
5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
