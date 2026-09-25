"""Erros de negócio e o manipulador global: qualquer falha vira um JSON com status, erro, rota, campos? e dica?."""
from typing import Optional

import psycopg
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


# Tradução das mensagens de validação do Pydantic ({max_length}, {ge} e {le} vêm do contexto do erro)
MENSAGENS = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Não pode ficar vazio.",
    "string_too_long": "Texto maior que o permitido (até {max_length} caracteres).",
    "string_type": "Esperava um texto aqui.",
    "url_parsing": "Informe uma URL válida (ex.: https://github.com/usuario).",
    "url_scheme": "A URL deve começar com http:// ou https://.",
    "url_type": "A URL precisa vir como texto, entre aspas.",
    "value_error": "Valor inválido.",
    "int_parsing": "Deve ser um número inteiro.",
    "int_type": "Use um número inteiro, sem aspas e sem casas decimais.",
    "int_from_float": "Use um número inteiro, sem casas decimais.",
    "greater_than": "Deve ser maior que zero.",
    "greater_than_equal": "O menor valor aceito é {ge}.",
    "less_than_equal": "O maior valor aceito é {le}.",
    "list_type": "Deve ser uma lista.",
    "model_type": "O corpo precisa ser um objeto JSON enviado com Content-Type: application/json.",
    "model_attributes_type": "O corpo precisa ser um objeto JSON enviado com Content-Type: application/json.",
}

# Campos com mensagem própria quando o Pydantic só diz "value_error"
MENSAGEM_DO_CAMPO = {"email": "Informe um e-mail válido."}

# Texto de cada status. "legenda" aparece no Swagger; "aviso" e "dica" vão na resposta
# quando quem recusa o pedido é o próprio framework (rota que não existe, método errado...)
STATUS_TEXTO = {
    400: {"legenda": "Pedido com algum dado fora da regra",
          "aviso": "O corpo da requisição veio num formato que a API não consegue abrir.",
          "dica": "Mande o corpo em JSON, codificado em UTF-8."},
    404: {"legenda": "Não achamos o registro (ou a rota)",
          "aviso": "Essa rota não existe na API.",
          "dica": "A lista de rotas está em /docs."},
    405: {"legenda": "Método que a rota não aceita",
          "aviso": "Essa rota existe, mas não aceita esse método.",
          "dica": "Veja em /docs se a rota usa GET, POST ou PUT."},
    409: {"legenda": "Cadastro que não pode se repetir"},
}


class BusinessError(Exception):
    status_code = 400

    def __init__(self, message: str):
        self.message = message


class NotFoundError(BusinessError):
    status_code = 404


class ConflictError(BusinessError):
    status_code = 409


class CorpoDeErro(BaseModel):
    """Como toda resposta de erro chega para quem chamou a API."""
    status: int
    erro: str
    rota: str
    campos: Optional[dict[str, str]] = None
    dica: Optional[str] = None


# Vai em todas as rotas pelo include_router: mostra o formato de erro no Swagger
# e, como já existe uma resposta "default", o FastAPI deixa de listar o 422
QUALQUER_ERRO = {"default": {"model": CorpoDeErro, "description": "Qualquer outro erro, sempre neste formato"}}


def _corpo(status_code: int, erro: str, rota: str,
           campos: Optional[dict] = None, dica: Optional[str] = None) -> dict:
    corpo = {"status": status_code, "erro": erro, "rota": rota}
    if campos:
        corpo["campos"] = campos
    if dica:
        corpo["dica"] = dica
    return corpo


def documentar_erro(status_code: int, erro: str, rota: str,
                    campos: Optional[dict] = None, dica: Optional[str] = None) -> dict:
    """Item do `responses` de uma rota: legenda do status e um exemplo de resposta."""
    return {
        "model": CorpoDeErro,
        "description": STATUS_TEXTO[status_code]["legenda"],
        "content": {"application/json": {"example": _corpo(status_code, erro, rota, campos, dica)}},
    }


def _responder(request: Request, status_code: int, erro: str, campos: Optional[dict] = None,
               dica: Optional[str] = None, headers: Optional[dict] = None) -> JSONResponse:
    rota = f"{request.method} {request.url.path}"
    return JSONResponse(status_code=status_code, content=_corpo(status_code, erro, rota, campos, dica),
                        headers=headers)


def _traduzir(err: dict) -> str:
    if err["type"] == "value_error":
        return MENSAGEM_DO_CAMPO.get(str(err["loc"][-1]), MENSAGENS["value_error"])
    texto = MENSAGENS.get(err["type"])
    if texto is None:
        return "Esse valor não foi aceito."  # nenhuma mensagem em inglês chega ao cliente
    return texto.format(**err.get("ctx", {}))


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessError)
    async def business_error(request: Request, exc: BusinessError):
        return _responder(request, exc.status_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # o FastAPI responderia 422; aqui a validação sempre volta como 400
        erros = exc.errors()
        quebrado = next((e for e in erros if e["type"] == "json_invalid"), None)
        if quebrado:
            posicao = quebrado["loc"][-1]
            return _responder(
                request, 400, "Não deu para entender o JSON enviado.",
                {"json": f"A leitura parou perto do caractere {posicao}."},
                dica="Em JSON, nomes de campo e textos vão entre aspas duplas.",
            )
        campos = {}
        for err in erros:
            # loc vem como ("body", "rating") ou ("query", "page"): o primeiro item só diz de onde veio
            campo = ".".join(str(parte) for parte in err["loc"][1:]) or "body"
            campos.setdefault(campo, _traduzir(err))
        return _responder(request, 400, "Os dados enviados são inválidos.", campos)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        texto = STATUS_TEXTO.get(exc.status_code, {})
        return _responder(request, exc.status_code, texto.get("aviso", "A requisição não pôde ser atendida."),
                          dica=texto.get("dica"), headers=getattr(exc, "headers", None))

    @app.exception_handler(psycopg.errors.UniqueViolation)
    async def unique_violation(request: Request, _: Exception):
        # os services já conferem e-mail e tecnologia antes; isto só pega dois cadastros iguais ao mesmo tempo
        return _responder(request, 409, "Esse valor já foi usado em outro cadastro e não pode se repetir.")

    @app.exception_handler(psycopg.errors.ForeignKeyViolation)
    async def foreign_key_violation(request: Request, _: Exception):
        return _responder(request, 404, "Algum registro ligado a este pedido não existe mais.")

    @app.exception_handler(psycopg.DataError)
    async def invalid_data(request: Request, _: Exception):
        # o caso mais comum é o caractere nulo (\u0000) num texto: o PostgreSQL não guarda esse caractere
        return _responder(request, 400, "O banco de dados recusou um dos valores enviados.",
                          dica="Textos não podem ter o caractere nulo (\\u0000).")

    @app.exception_handler(psycopg.OperationalError)
    async def database_unavailable(request: Request, _: Exception):
        return _responder(request, 503, "Sem conexão com o banco de dados agora.",
                          dica="Espere alguns segundos e tente de novo.")

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, _: Exception):
        # o erro completo aparece no terminal do uvicorn; quem chamou recebe só a frase genérica
        return _responder(request, 500, "Algo falhou aqui no servidor e o pedido não foi concluído.")
