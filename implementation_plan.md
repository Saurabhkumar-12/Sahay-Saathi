# Sahay Saathi Intent Router Implementation Plan

This plan details transitioning Sahay Saathi from a category-based direct scheme matching system to an **Intent Router** architecture. We will analyze intent first, handle confidence levels and live-data needs, and perform context-aware response generation with actionable next steps.

## User Review Required

> [!IMPORTANT]
> - **Primary Routing:** The backend will route queries based on classified *intent* rather than *userType* directly. `userType` will act strictly as auxiliary context.
> - **Extensible Architecture:** We will introduce an `IntentRouter` service using structured JSON classification.
> - **Rich Responses:** We will add `intent` and `actionable_next_step` to the response schema to allow the UI to react to the context.

## Open Questions

None. The list of 22 intents, confidence requirements, and output schemas are fully specified.

## Proposed Changes

### Backend Intent Routing & Verification

We will introduce the Intent Router, adjust validation schemas, update services, and add comprehensive integration tests.

#### [MODIFY] [backend/app/schemas.py](file:///e:/Sahay Saathi/backend/app/schemas.py)
- Introduce `IntentRoutingInfo` schema:
  ```python
  class IntentRoutingInfo(BaseModel):
      intent: str
      confidence: float
      needsClarification: bool
      needsLocation: bool
      needsLiveData: bool
  ```
- Update `ChatResponse` to include `intent` and `actionable_next_step`:
  ```python
  class ChatResponse(BaseModel):
      answer: str
      sources: List[SchemeSource] = []
      warning: str
      language: str
      intent: str
      actionable_next_step: Optional[str] = None
  ```

#### [NEW] [backend/app/services/router.py](file:///e:/Sahay Saathi/backend/app/services/router.py)
- Create `IntentRouter` using the Gemini API structured output model to classify client input into one of the 22 supported intents.
- Check confidence levels and set `needsClarification` or flags if required details are missing.

#### [MODIFY] [backend/app/services/gemini.py](file:///e:/Sahay Saathi/backend/app/services/gemini.py)
- Update `generate_assistance` to invoke the `IntentRouter` pipeline.
- Ground information:
  - If intent is scheme/eligibility related, query the local database.
  - If intent is live-data related (e.g., weather, market prices, sea safety) and not grounded in source data, return a polite limitation warning rather than hallucinating.
  - If `needsClarification` is True, prompt the user for clarifying details.
- Provide simple language translations and an actionable next step for the user.

#### [MODIFY] [backend/tests/test_api.py](file:///e:/Sahay Saathi/backend/tests/test_api.py)
- Add backend test cases covering key intents across multiple user categories:
  - `Farmer + PM Kisan` -> `government_scheme`
  - `Farmer + water shortage` -> `irrigation`
  - `Farmer + rain` -> `weather`
  - `Farmer + crop disease` -> `crop_health`
  - `Farmer + crop price` -> `market_price`
  - `Street Vendor + loan` -> `financial_support`
  - `Street Vendor + stock decision` -> `inventory`
  - `Artisan + pricing` -> `pricing`
  - `Artisan + selling online` -> `market_access`
  - `Fisherman + sea safety` -> `safety`
  - `Rural Worker + skill training` -> `skill_development`
  - `Person with Disability + accessible service` -> `accessibility`
  - `Citizen + pension` -> `government_service`

---

### Frontend Adapters

We will update the UI to display the classified intent type and the actionable next step.

#### [MODIFY] [frontend/src/components/ChatInterface.jsx](file:///e:/Sahay Saathi/frontend/src/components/ChatInterface.jsx)
- Display the actionable next step clearly at the bottom of the assistant's message card.
- Adapt the UI icons or badges based on the returned query `intent`.

## Verification Plan

### Automated Tests
- Run the expanded test suite using pytest to verify 100% routing accuracy:
  ```bash
  pytest backend/tests/
  ```

### Manual Verification
- Deploy and verify that the UI renders the correct intent classification and actionable next step alerts.
- Check rate limiter performance.
