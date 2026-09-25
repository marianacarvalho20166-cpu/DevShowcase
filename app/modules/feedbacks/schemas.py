from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.types import RequiredText


class FeedbackCreate(BaseModel):
    """DTO de entrada de um feedback: nota de 1 a 5 e comentário."""
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "author_name": "Mariana Gomes Carvalho",
        "comment": "Interface simples e o cardápio carrega rápido no celular.",
        "rating": 5,
    }]})

    author_name: RequiredText
    comment: RequiredText
    rating: int = Field(ge=1, le=5, strict=True)  # strict: recusa true, "4" e 4.0 em vez de converter


class FeedbackResponse(BaseModel):
    id: int
    author_name: str
    comment: str
    rating: int
    created_at: datetime


class FeedbackCreated(BaseModel):
    """DTO de saída do cadastro: o feedback salvo e a nova média do projeto."""
    project_id: int
    feedback: FeedbackResponse
    average_rating: float
    ratings_count: int
