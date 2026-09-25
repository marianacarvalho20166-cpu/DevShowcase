"""Erros de negócio e formatação padronizada das respostas de erro."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# Tradução das mensagens de validação mais comuns do Pydantic
MENSAGENS = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Não pode ficar vazio.",
    "string_too_long": "Texto maior que o permitido.",
    "url_parsing": "Informe uma URL válida (ex.: https://github.com/usuario).",
    "url_scheme": "A URL deve começar com http:// ou https://.",
    "value_error": "Valor inválido.",
    "int_parsing": "Deve ser um número inteiro.",
    "greater_than": "Deve ser maior que zero.",
    "list_type": "Deve ser uma lista.",
}


class BusinessError(Exception):
    status_code = 400

    def __init__(self, message: str):
        self.message = message


class NotFoundError(BusinessError):
    status_code = 404


class ConflictError(BusinessError):
    status_code = 409


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessError)
    async def business_error(_: Request, exc: BusinessError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": exc.status_code, "erro": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        campos = {}
        for err in exc.errors():
            nome = ".".join(str(p) for p in err["loc"] if p != "body") or "body"
            if err["type"] == "value_error" and "email" in nome:
                campos[nome] = "Informe um e-mail válido."
            else:
                campos[nome] = MENSAGENS.get(err["type"], err["msg"])
        return JSONResponse(
            status_code=422,
            content={"status": 422, "erro": "Os dados enviados são inválidos.", "campos": campos},
        )
