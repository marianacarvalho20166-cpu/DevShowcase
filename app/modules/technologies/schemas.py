from typing import Optional

from pydantic import BaseModel

from app.core.types import RequiredText


class TechnologyCreate(BaseModel):
    """DTO de entrada para cadastrar uma tecnologia."""
    name: RequiredText
    category: Optional[RequiredText] = None  # ex.: Linguagem, Framework, Banco de dados


class TechnologyResponse(BaseModel):
    """DTO de saída de uma tecnologia."""
    id: int
    name: str
    category: Optional[str] = None
