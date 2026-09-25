"""DevShowcase API — Grupo 4 (Python + FastAPI + PostgreSQL)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.database import init_db
from app.core.errors import QUALQUER_ERRO, register_error_handlers
from app.modules.feedbacks.router import router as feedbacks_router
from app.modules.profiles.router import router as profiles_router
from app.modules.projects.router import router as projects_router
from app.modules.technologies.router import router as technologies_router

SOBRE_A_API = """
Vitrine de projetos feita pelo **Grupo 4**: Elismar Francelina de Carvalho, Mariana Gomes Carvalho
e Kaenny Ribeiro Granja.

**Por onde começar?** Siga os grupos de rotas na ordem em que aparecem: crie um perfil, cadastre as
tecnologias, publique um projeto e depois dê estrelas e deixe feedbacks. Em cada rota, clique em
*Try it out*, mude o exemplo se quiser e clique em *Execute*.

**E se der erro?** A resposta sempre traz `status`, `erro` e `rota`. Quando algum dado precisa ser
corrigido aparece também `campos`, e quando temos uma sugestão aparece `dica`:

```json
{
  "status": 400,
  "erro": "Os dados enviados são inválidos.",
  "rota": "POST /api/projects/3/feedbacks",
  "campos": { "rating": "O maior valor aceito é 5." }
}
```

Códigos usados: `400` pedido com dado errado (inclusive JSON quebrado e parâmetro de página inválido),
`404` registro ou rota que não existe, `405` método que a rota não aceita, `409` cadastro repetido,
`500` falha inesperada (sem detalhes internos) e `503` banco de dados fora do ar.
"""

GRUPOS_DE_ROTAS = [
    {"name": "Perfis", "description": "Passo 1: quem publica os projetos. O perfil mostra os projetos da pessoa."},
    {"name": "Tecnologias", "description": "Passo 2: linguagens, frameworks e bancos que um projeto pode usar."},
    {"name": "Projetos", "description": "Passo 3: publicar, procurar por tecnologia (com páginas) e dar estrelas."},
    {"name": "Feedbacks", "description": "Passo 4: feedbacks (comentário + nota); a média do projeto é refeita a cada um."},
    {"name": "Status", "description": "Serve para acordar a API no Render antes de testar."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # cria as tabelas se o banco estiver vazio
    yield


app = FastAPI(
    title="DevShowcase API — Grupo 4",
    description=SOBRE_A_API,
    version="2.0.0",
    openapi_tags=GRUPOS_DE_ROTAS,
    lifespan=lifespan,
)

register_error_handlers(app)
# QUALQUER_ERRO documenta o formato de erro em todas as rotas e faz o FastAPI parar de listar o 422 no Swagger
for router in (profiles_router, technologies_router, projects_router, feedbacks_router):
    app.include_router(router, responses=QUALQUER_ERRO)


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def ir_para_docs():
    return RedirectResponse("/docs")


@app.get("/health", tags=["Status"], summary="A API acordou?", response_description="Acordou e está respondendo")
def health():
    return {"status": "ok"}
