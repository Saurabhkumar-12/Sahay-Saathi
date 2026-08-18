import os
import traceback
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.schemas import ChatRequest, ChatResponse
from app.services.gemini import generate_assistance

# Load environment variables
load_dotenv()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Sahay Saathi API")
app.state.limiter = limiter

# Rate limit configuration
RATE_LIMIT_REQUESTS = os.getenv("RATE_LIMIT_REQUESTS", "20")
RATE_LIMIT_WINDOW_SECONDS = os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
limit_str = f"{RATE_LIMIT_REQUESTS} per {RATE_LIMIT_WINDOW_SECONDS} second"

# Register rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler to shield users from tracebacks/internal details
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Server Error occurred on {request.url.path}:")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(limit_str)
async def chat_endpoint(payload: ChatRequest, request: Request):
    try:
        response = await generate_assistance(payload)
        return response
    except ValueError as val_err:
        # Pydantic or custom validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err)
        )
    except Exception as e:
        print(f"Error handling chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate assistance. Please try again."
        )
