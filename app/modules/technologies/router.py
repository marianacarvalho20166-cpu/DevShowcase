from fastapi import APIRouter, status

from app.core.database import DbConnection
from app.core.errors import documentar_erro
from .schemas import TechnologyCreate, TechnologyResponse
from .service import TechnologyService

router = APIRouter(prefix="/api/technologies", tags=["Tecnologias"])


@router.post(
    "",
    response_model=TechnologyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar uma tecnologia",
    response_description="Tecnologia cadastrada",
    description=(
        "A categoria é opcional (Linguagem, Framework, Banco de dados...). Se já existir uma "
        "tecnologia com o mesmo nome, mesmo escrita de outro jeito (fastapi e FastAPI), a resposta é 409."
    ),
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "POST /api/technologies",
                             {"name": "Campo obrigatório."}),
        409: documentar_erro(409, "A tecnologia 'fastapi' já está cadastrada.", "POST /api/technologies"),
    },
)
def create_technology(body: TechnologyCreate, db: DbConnection):
    return TechnologyService(db).create(body)


@router.get(
    "",
    response_model=list[TechnologyResponse],
    summary="Ver todas as tecnologias",
    response_description="Lista completa, ordenada pelo nome",
    description="Devolve tudo o que já foi cadastrado, ordenado pelo nome. É daqui que saem os números do `technology_ids`.",
)
def list_technologies(db: DbConnection):
    return TechnologyService(db).list_all()
