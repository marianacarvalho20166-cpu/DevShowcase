from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl

from app.core.types import OptionalText, RequiredText


class ProfileCreate(BaseModel):
    """DTO de entrada para cadastrar um perfil de desenvolvedor."""
    full_name: RequiredText
    email: EmailStr
    headline: Optional[OptionalText] = None   # ex.: "Desenvolvedora back-end"
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None


class ProjectSummary(BaseModel):
    """Resumo de projeto exibido dentro do perfil."""
    id: int
    title: str
    repo_url: str


class ProfileResponse(BaseModel):
    """DTO de saída de um perfil, com os projetos dele (relação 1:N)."""
    id: int
    full_name: str
    email: str
    headline: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    created_at: str
    total_projects: int
    projects: list[ProjectSummary]
