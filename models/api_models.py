from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    """Pydantic model for the summarize request payload."""
    video_url: str
    summary_length: int
    used_model: str


class UserCreate(BaseModel):
    """Pydantic model for user registration payload."""
    username: str
    email: str
    password: str
