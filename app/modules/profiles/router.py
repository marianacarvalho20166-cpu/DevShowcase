from fastapi import APIRouter, status

from app.core.database import DbConnection
from app.core.errors import documentar_erro
from .schemas import ProfileCreate, ProfileResponse
from .service import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["Perfis"])


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar uma pessoa desenvolvedora",
    response_description="Perfil criado (ainda sem projetos)",
    description=(
        "Só `full_name` e `email` são obrigatórios. Cada e-mail só pode ter um perfil, e "
        "maiúsculas não contam como diferença (Ana@email.com = ana@email.com)."
    ),
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "POST /api/profiles",
                             {"email": "Informe um e-mail válido.",
                              "linkedin_url": "Informe uma URL válida (ex.: https://github.com/usuario)."}),
        409: documentar_erro(409, "Já existe um perfil com esse e-mail.", "POST /api/profiles"),
    },
)
def create_profile(body: ProfileCreate, db: DbConnection):
    return ProfileService(db).create(body)


@router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Abrir um perfil com os projetos da pessoa",
    response_description="O perfil e o resumo dos projetos dele",
    description="Traz o perfil, o total de projetos e um resumo de cada um (relação 1:N).",
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "GET /api/profiles/xyz",
                             {"profile_id": "Deve ser um número inteiro."}),
        404: documentar_erro(404, "Perfil 424242 não encontrado.", "GET /api/profiles/424242"),
    },
)
def get_profile(profile_id: int, db: DbConnection):
    return ProfileService(db).get(profile_id)
