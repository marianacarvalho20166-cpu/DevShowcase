from pydantic import BaseModel, Field

from app.core.types import RequiredText


class FeedbackCreate(BaseModel):
    """DTO de entrada de um feedback (será usado nas próximas etapas)."""
    author_name: RequiredText
    comment: RequiredText
    rating: int = Field(ge=1, le=5)


class FeedbackResponse(BaseModel):
    id: int
    author_name: str
    comment: str
    rating: int
    created_at: str
