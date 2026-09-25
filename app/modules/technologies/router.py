from fastapi import APIRouter, status

from app.core.database import DbConnection
from app.core.errors import doc_erro
from .schemas import TechnologyCreate, TechnologyResponse
from .service import TechnologyService

router = APIRouter(prefix="/api/technologies", tags=["Tecnologias"])


@router.post(
    "",
    response_model=TechnologyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar tecnologia",
    response_description="Tecnologia cadastrada",
    description="Cadastra uma linguagem, framework ou banco. O nome não pode se repetir (sem diferenciar maiúsculas).",
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "POST /api/technologies",
                      {"name": "Não pode ficar vazio."}),
        409: doc_erro(409, "A tecnologia 'PYTHON' já está cadastrada.", "POST /api/technologies"),
    },
)
def create_technology(body: TechnologyCreate, db: DbConnection):
    return TechnologyService(db).create(body)


@router.get(
    "",
    response_model=list[TechnologyResponse],
    summary="Listar tecnologias",
    response_description="Tecnologias em ordem alfabética",
    description="Lista todas as tecnologias em ordem alfabética.",
)
def list_technologies(db: DbConnection):
    return TechnologyService(db).list_all()
