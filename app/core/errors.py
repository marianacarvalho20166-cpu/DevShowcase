"""Erros de negócio e manipulador global: toda resposta de erro sai no mesmo formato."""
from typing import Optional

import psycopg
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


# Tradução das mensagens de validação do Pydantic ({ge}, {le}... vêm do contexto do erro)
MENSAGENS = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Não pode ficar vazio.",
    "string_too_long": "Texto maior que o permitido (máximo de {max_length} caracteres).",
    "string_type": "Deve ser um texto.",
    "url_parsing": "Informe uma URL válida (ex.: https://github.com/usuario).",
    "url_scheme": "A URL deve começar com http:// ou https://.",
    "url_type": "Informe a URL como texto.",
    "value_error": "Valor inválido.",
    "int_parsing": "Deve ser um número inteiro.",
    "int_type": "Deve ser um número inteiro.",
    "int_from_float": "Deve ser um número inteiro, sem casas decimais.",
    "greater_than": "Deve ser maior que {gt}.",
    "greater_than_equal": "Deve ser no mínimo {ge}.",
    "less_than": "Deve ser menor que {lt}.",
    "less_than_equal": "Deve ser no máximo {le}.",
    "list_type": "Deve ser uma lista.",
    "model_type": "Envie um objeto JSON com o cabeçalho Content-Type: application/json.",
    "model_attributes_type": "Envie um objeto JSON com o cabeçalho Content-Type: application/json.",
    "dict_type": "Deve ser um objeto JSON.",
    "json_invalid": "JSON malformado: confira aspas, vírgulas e chaves.",
    "null_char": "Contém um caractere inválido.",
}

MENSAGENS_HTTP = {
    400: "Não foi possível ler o corpo da requisição. Envie um JSON válido em UTF-8.",
    404: "Rota não encontrada. Confira o endereço e o método na documentação em /docs.",
    405: "Método HTTP não permitido nesta rota.",
}

# Nome do índice único no banco -> mensagem de conflito
MENSAGENS_UNICIDADE = {
    "uq_profiles_email": "Já existe um perfil com esse e-mail.",
    "uq_technologies_name": "Essa tecnologia já está cadastrada.",
}

DESCRICOES_DOC = {
    400: "Dados ou parâmetros inválidos",
    404: "Registro não encontrado",
    409: "Registro repetido",
}


class BusinessError(Exception):
    status_code = 400

    def __init__(self, message: str):
        self.message = message


class NotFoundError(BusinessError):
    status_code = 404


class ConflictError(BusinessError):
    status_code = 409


class ErroResposta(BaseModel):
    """Formato padrão de todas as respostas de erro."""
    status: int
    erro: str
    campos: Optional[dict[str, str]] = None
    rota: str


def doc_erro(status_code: int, erro: str, rota: str, campos: Optional[dict] = None) -> dict:
    """Documenta no Swagger uma resposta de erro, com exemplo."""
    exemplo = {"status": status_code, "erro": erro}
    if campos:
        exemplo["campos"] = campos
    exemplo["rota"] = rota
    return {
        "model": ErroResposta,
        "description": DESCRICOES_DOC.get(status_code, erro),
        "content": {"application/json": {"example": exemplo}},
    }


def _resposta(request: Request, status_code: int, erro: str,
              campos: Optional[dict] = None, headers: Optional[dict] = None) -> JSONResponse:
    content = {"status": status_code, "erro": erro}
    if campos:
        content["campos"] = campos
    content["rota"] = f"{request.method} {request.url.path}"
    return JSONResponse(status_code=status_code, content=content, headers=headers)


def _traduzir(err: dict, campo: str) -> str:
    if err["type"] == "value_error" and "email" in campo:
        return "Informe um e-mail válido."
    modelo = MENSAGENS.get(err["type"], "Valor inválido.")
    try:
        return modelo.format(**err.get("ctx", {}))
    except (KeyError, IndexError):
        return modelo


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessError)
    async def business_error(request: Request, exc: BusinessError):
        return _resposta(request, exc.status_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # o FastAPI responderia 422; aqui toda falha de validação vira 400
        campos = {}
        for err in exc.errors():
            if err["type"] == "json_invalid":
                return _resposta(request, 400, "O corpo da requisição não é um JSON válido.",
                                 {"body": MENSAGENS["json_invalid"]})
            campo = ".".join(str(p) for p in err["loc"][1:]) or "body"  # tira "body"/"query"/"path"
            campos.setdefault(campo, _traduzir(err, campo))
        return _resposta(request, 400, "Os dados enviados são inválidos.", campos)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        erro = MENSAGENS_HTTP.get(exc.status_code, "Não foi possível atender a requisição.")
        return _resposta(request, exc.status_code, erro, headers=getattr(exc, "headers", None))

    @app.exception_handler(psycopg.errors.UniqueViolation)
    async def unique_violation(request: Request, exc: psycopg.errors.UniqueViolation):
        erro = MENSAGENS_UNICIDADE.get(exc.diag.constraint_name, "Já existe um registro com esses dados.")
        return _resposta(request, 409, erro)

    @app.exception_handler(psycopg.errors.ForeignKeyViolation)
    async def foreign_key_violation(request: Request, _: Exception):
        return _resposta(request, 404, "Um dos registros relacionados não foi encontrado.")

    @app.exception_handler(psycopg.DataError)
    async def invalid_data(request: Request, _: Exception):
        # ex.: caractere nulo (\u0000) num texto, que o PostgreSQL não aceita
        return _resposta(request, 400, "Os dados enviados contêm caracteres ou valores inválidos.")

    @app.exception_handler(psycopg.OperationalError)
    async def database_unavailable(request: Request, _: Exception):
        return _resposta(request, 503, "Banco de dados indisponível no momento. Tente novamente em instantes.")

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, _: Exception):
        # o detalhe fica só no log do servidor, nunca na resposta
        return _resposta(request, 500, "Erro interno no servidor. Tente novamente mais tarde.")
