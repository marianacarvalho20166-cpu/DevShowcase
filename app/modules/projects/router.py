from typing import Annotated, Optional

from fastapi import APIRouter, Query, status

from app.core.database import DbConnection
from app.core.errors import documentar_erro
from app.core.types import FilterText
from .schemas import ProjectCreate, ProjectListing, ProjectResponse
from .service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["Projetos"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Publicar um projeto na vitrine",
    response_description="Projeto publicado, já com dono e tecnologias",
    description=(
        "Informe em `profile_id` quem fez o projeto e em `technology_ids` os ids das tecnologias "
        "usadas (id repetido é ignorado). Todo projeto começa com 0 estrelas e sem média."
    ),
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "POST /api/projects",
                             {"repo_url": "A URL deve começar com http:// ou https://.",
                              "technology_ids": "Deve ser uma lista."}),
        404: documentar_erro(404, "Perfil 424242 não encontrado.", "POST /api/projects"),
    },
)
def create_project(body: ProjectCreate, db: DbConnection):
    return ProjectService(db).create(body)


@router.get(
    "",
    response_model=ProjectListing,
    summary="Ver os projetos (com páginas e busca por tecnologia)",
    response_description="Os totais do filtro e os projetos da página pedida",
    description=(
        "Os projetos publicados por último aparecem primeiro. Quer só os que usam FastAPI? "
        "Use `?tech=fastapi` (tanto faz escrever fastapi, FastAPI ou FASTAPI). Para andar pela "
        "lista, combine `page` e `per_page`. Uma página depois da última não dá erro: `results` "
        "volta como lista vazia e os totais continuam certos."
    ),
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "GET /api/projects",
                             {"per_page": "O menor valor aceito é 1."}),
    },
)
def list_projects(
    db: DbConnection,
    tech: Annotated[Optional[FilterText], Query(description="Tecnologia que o projeto precisa usar.",
                                                examples=["fastapi"])] = None,
    page: Annotated[int, Query(ge=1, description="Qual página ver (a primeira é a 1).")] = 1,
    per_page: Annotated[int, Query(ge=1, le=20, description="Tamanho da página (mínimo 1, máximo 20).")] = 5,
):
    return ProjectService(db).list_filtered(tech, page, per_page)


@router.put(
    "/{project_id}/upvote",
    response_model=ProjectResponse,
    summary="Dar uma estrela a um projeto",
    response_description="Projeto com a estrela já contada",
    description=(
        "Vai sem corpo: cada chamada soma 1 em `stars`. Quem soma é o PostgreSQL, no comando "
        "`UPDATE projects SET stars = stars + 1`, então duas pessoas clicando juntas dão duas estrelas."
    ),
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "PUT /api/projects/xyz/upvote",
                             {"project_id": "Deve ser um número inteiro."}),
        404: documentar_erro(404, "Nenhum projeto tem o id 424242.", "PUT /api/projects/424242/upvote"),
    },
)
def star_project(project_id: int, db: DbConnection):
    return ProjectService(db).give_star(project_id)
