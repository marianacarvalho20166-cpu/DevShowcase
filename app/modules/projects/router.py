from typing import Annotated, Optional

from fastapi import APIRouter, Query, status

from app.core.database import DbConnection
from app.core.errors import doc_erro
from app.core.types import FilterText
from .schemas import ProjectCreate, ProjectPage, ProjectResponse
from .service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["Projetos"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar projeto",
    response_description="Projeto cadastrado",
    description="Cadastra um projeto ligado a um perfil e às tecnologias usadas (relação N:N).",
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "POST /api/projects",
                      {"title": "Não pode ficar vazio.", "repo_url": "Informe uma URL válida (ex.: https://github.com/usuario)."}),
        404: doc_erro(404, "Perfil 999 não encontrado.", "POST /api/projects"),
    },
)
def create_project(body: ProjectCreate, db: DbConnection):
    return ProjectService(db).create(body)


@router.get(
    "",
    response_model=ProjectPage,
    summary="Listar projetos com filtro por tecnologia e paginação",
    response_description="Página de projetos",
    description=(
        "Lista os projetos do mais novo para o mais antigo. Use `tech` para filtrar pelo nome da "
        "tecnologia (sem diferenciar maiúsculas) e `page`/`per_page` para paginar. "
        "Uma página além do fim devolve `results` vazio."
    ),
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "GET /api/projects",
                      {"page": "Deve ser no mínimo 1.", "per_page": "Deve ser no máximo 20."}),
    },
)
def list_projects(
    db: DbConnection,
    tech: Annotated[Optional[FilterText], Query(description="Nome da tecnologia (ex.: python, PYTHON, Python).",
                                                examples=["python"])] = None,
    page: Annotated[int, Query(ge=1, description="Número da página, começando em 1.")] = 1,
    per_page: Annotated[int, Query(ge=1, le=20, description="Itens por página (1 a 20).")] = 5,
):
    return ProjectService(db).list_page(tech, page, per_page)


@router.put(
    "/{project_id}/upvote",
    response_model=ProjectResponse,
    summary="Dar uma estrela ao projeto (upvote)",
    response_description="Projeto com a estrela somada",
    description="Soma 1 às estrelas do projeto com incremento atômico no banco (`stars = stars + 1`).",
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "PUT /api/projects/abc/upvote",
                      {"project_id": "Deve ser um número inteiro."}),
        404: doc_erro(404, "Projeto 999 não encontrado.", "PUT /api/projects/999/upvote"),
    },
)
def upvote_project(project_id: int, db: DbConnection):
    return ProjectService(db).upvote(project_id)
