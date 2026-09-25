"""Tipos reutilizados pelos DTOs de entrada."""
from typing import Annotated

from pydantic import StringConstraints

# Texto obrigatório: remove espaços das pontas e exige pelo menos 1 caractere
RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
OptionalText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
