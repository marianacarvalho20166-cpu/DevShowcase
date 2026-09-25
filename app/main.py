"""DevShowcase API — Grupo 4 (Python + FastAPI + SQLite)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.core.errors import register_error_handlers
from app.modules.profiles.router import router as profiles_router
from app.modules.projects.router import router as projects_router
from app.modules.technologies.router import router as technologies_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # cria as tabelas na primeira execução
    yield


app = FastAPI(
    title="DevShowcase API — Grupo 4",
    description="Vitrine de projetos de desenvolvedores: perfis, projetos, tecnologias e feedbacks.",
    version="1.0.0",
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(profiles_router)
app.include_router(technologies_router)
app.include_router(projects_router)


@app.get("/health", tags=["Status"])
def health():
    return {"status": "ok"}
