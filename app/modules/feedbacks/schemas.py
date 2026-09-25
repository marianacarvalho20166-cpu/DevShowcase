from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from app.core.types import RequiredText


class FeedbackCreate(BaseModel):
    """DTO de entrada do feedback: quem avaliou, o comentário e a nota."""
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "author_name": "Mariana Gomes Carvalho",
        "comment": "Marquei o banho da minha cachorra em dois cliques.",
        "rating": 5,
    }]})

    author_name: RequiredText
    comment: RequiredText
    rating: StrictInt = Field(ge=1, le=5)


class FeedbackResponse(BaseModel):
    id: int
    author_name: str
    comment: str
    rating: int
    created_at: datetime


class FeedbackCreated(BaseModel):
    """DTO de saída do cadastro: o feedback guardado e como ficou a média do projeto."""
    project_id: int
    feedback: FeedbackResponse
    average_rating: float
    ratings_count: int
