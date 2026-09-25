from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.core.types import OptionalText, RequiredText
from app.modules.feedbacks.schemas import FeedbackResponse
from app.modules.technologies.schemas import TechnologyResponse


class ProjectCreate(BaseModel):
    """DTO de entrada para cadastrar um projeto no portfólio."""
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "profile_id": 1,
        "title": "Controle de Academia",
        "summary": "Alunos, planos e mensalidades de uma academia de bairro",
        "repo_url": "https://github.com/kaennygranja/controle-academia",
        "live_url": None,
        "technology_ids": [1, 2, 3],
    }]})

    profile_id: int = Field(gt=0)
    title: RequiredText
    summary: Optional[OptionalText] = None
    repo_url: HttpUrl
    live_url: Optional[HttpUrl] = None
    technology_ids: list[int] = Field(default_factory=list)

    @field_validator("technology_ids")
    @classmethod
    def remove_duplicates(cls, ids: list[int]) -> list[int]:
        return list(dict.fromkeys(ids))  # mantém a ordem e tira repetidos


class ProjectOwner(BaseModel):
    id: int
    full_name: str


class ProjectResponse(BaseModel):
    """DTO de saída de um projeto: dono, tecnologias (N:N) e feedbacks (1:N)."""
    id: int
    title: str
    summary: Optional[str] = None
    repo_url: str
    live_url: Optional[str] = None
    stars: int
    average_rating: Optional[float] = None   # sem nenhum feedback ainda: null
    created_at: datetime
    owner: ProjectOwner
    technologies: list[TechnologyResponse]
    feedbacks: list[FeedbackResponse]


class ProjectListing(BaseModel):
    """Resultado da listagem: os totais do filtro e os projetos da página pedida."""
    total: int
    page: int
    per_page: int
    total_pages: int
    results: list[ProjectResponse]
