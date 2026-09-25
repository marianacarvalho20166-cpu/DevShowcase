from fastapi import APIRouter, status

from app.core.database import DbConnection
from app.core.errors import doc_erro
from .schemas import ProfileCreate, ProfileResponse
from .service import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["Perfis"])


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar perfil",
    response_description="Perfil cadastrado",
    description="Cadastra o perfil de um desenvolvedor. O e-mail precisa ser válido e não pode se repetir.",
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "POST /api/profiles",
                      {"full_name": "Não pode ficar vazio.", "email": "Informe um e-mail válido."}),
        409: doc_erro(409, "Já existe um perfil com esse e-mail.", "POST /api/profiles"),
    },
)
def create_profile(body: ProfileCreate, db: DbConnection):
    return ProfileService(db).create(body)


@router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Buscar perfil com seus projetos",
    response_description="Perfil com seus projetos",
    description="Retorna o perfil e a lista resumida dos projetos dele (relação 1:N).",
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "GET /api/profiles/abc",
                      {"profile_id": "Deve ser um número inteiro."}),
        404: doc_erro(404, "Perfil 999 não encontrado.", "GET /api/profiles/999"),
    },
)
def get_profile(profile_id: int, db: DbConnection):
    return ProfileService(db).get(profile_id)
