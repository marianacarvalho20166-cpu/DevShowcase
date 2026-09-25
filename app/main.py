"""DevShowcase API — Grupo 4 (Python + FastAPI + PostgreSQL)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.database import init_db
from app.core.errors import register_error_handlers
from app.modules.feedbacks.router import router as feedbacks_router
from app.modules.profiles.router import router as profiles_router
from app.modules.projects.router import router as projects_router
from app.modules.technologies.router import router as technologies_router

DESCRICAO = """
Vitrine de projetos de desenvolvedores do **Grupo 4** — Elismar Francelina de Carvalho,
Mariana Gomes Carvalho e Kaenny Ribeiro Granja.

Cada desenvolvedor tem um **perfil**, publica **projetos** ligados às **tecnologias** usadas
e recebe **feedbacks** (nota de 1 a 5 com comentário) e **estrelas**.

**Para testar aqui:** abra uma rota, clique em *Try it out*, ajuste o exemplo e clique em *Execute*.

**Formato dos erros** (igual em todas as rotas):

```json
{
  "status": 400,
  "erro": "Os dados enviados são inválidos.",
  "campos": { "rating": "Deve ser no máximo 5." },
  "rota": "POST /api/projects/1/feedbacks"
}
```

`400` dados ou parâmetros inválidos (inclusive JSON malformado) · `404` registro ou rota inexistente ·
`409` registro repetido · `500` erro interno (sem expor detalhes) · `503` banco de dados fora do ar.
"""

TAGS = [
    {"name": "Projetos", "description": "Cadastro de projetos, listagem com filtro por tecnologia e paginação, e estrelas (upvote)."},
    {"name": "Feedbacks", "description": "Avaliações dos projetos. Cada feedback recalcula a nota média do projeto."},
    {"name": "Perfis", "description": "Perfis dos desenvolvedores, com os projetos de cada um."},
    {"name": "Tecnologias", "description": "Linguagens, frameworks e bancos que podem ser ligados aos projetos."},
    {"name": "Status", "description": "Confere se a API está no ar."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # cria as tabelas se o banco estiver vazio
    yield


app = FastAPI(
    title="DevShowcase API — Grupo 4",
    description=DESCRICAO,
    version="2.0.0",
    openapi_tags=TAGS,
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(projects_router)
app.include_router(feedbacks_router)
app.include_router(profiles_router)
app.include_router(technologies_router)


def openapi_sem_422() -> dict:
    """A API responde 400 nas validações, então o 422 automático sai da documentação."""
    if app.openapi_schema is None:
        schema = FastAPI.openapi(app)
        for operacoes in schema["paths"].values():
            for operacao in operacoes.values():
                operacao.get("responses", {}).pop("422", None)
        for nome in ("HTTPValidationError", "ValidationError"):
            schema.get("components", {}).get("schemas", {}).pop(nome, None)
    return app.openapi_schema


app.openapi = openapi_sem_422


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.get("/health", tags=["Status"], summary="Verificar se a API está no ar", response_description="API no ar")
def health():
    return {"status": "ok"}
