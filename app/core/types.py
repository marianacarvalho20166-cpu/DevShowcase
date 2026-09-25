"""Tipos reutilizados pelos DTOs de entrada."""
from typing import Annotated

from pydantic import AfterValidator, StringConstraints
from pydantic_core import PydanticCustomError


def _reject_null_char(text: str) -> str:
    # o PostgreSQL não guarda o caractere nulo (\u0000): recusa aqui com 400 antes de chegar no banco
    if "\x00" in text:
        raise PydanticCustomError("null_char", "Contém um caractere inválido.")
    return text


NoNullChar = AfterValidator(_reject_null_char)

# Texto obrigatório: remove espaços das pontas e exige pelo menos 1 caractere
RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150), NoNullChar]
OptionalText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500), NoNullChar]
# Texto de filtro na URL (ex.: ?tech=python)
FilterText = Annotated[str, StringConstraints(max_length=50), NoNullChar]
