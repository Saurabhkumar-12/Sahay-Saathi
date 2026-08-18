from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_LANGUAGES = {"en", "hi", "hinglish"}
ALLOWED_USER_TYPES = {
    "farmer",
    "street vendor",
    "artisan",
    "fisherman",
    "rural worker",
    "person with disability",
    "citizen",
    "other"
}

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The query string sent by the user."
    )
    language: str = Field(
        ...,
        description="Target language. Must be 'en', 'hi', or 'hinglish'."
    )
    userType: str = Field(
        ...,
        description="User classification to provide query context."
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or only whitespace.")
        return stripped

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        val_lower = value.strip().lower()
        if val_lower not in ALLOWED_LANGUAGES:
            raise ValueError(f"Invalid language. Allowed options are: {', '.join(ALLOWED_LANGUAGES)}")
        return val_lower

    @field_validator("userType")
    @classmethod
    def validate_user_type(cls, value: str) -> str:
        val_lower = value.strip().lower()
        if val_lower not in ALLOWED_USER_TYPES:
            raise ValueError(f"Invalid user type. Allowed options are: {', '.join(ALLOWED_USER_TYPES)}")
        return val_lower

class SchemeSource(BaseModel):
    name: str = Field(..., description="Official scheme name.")
    url: str = Field(..., description="Official website URL.")
    last_verified: Optional[str] = Field(None, description="Last date verified.")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI generated grounded response.")
    sources: List[SchemeSource] = Field(default=[], description="List of source schemes used.")
    warning: str = Field(..., description="Safety or verification warning message.")
    language: str = Field(..., description="Response language indicator.")
