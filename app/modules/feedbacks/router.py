from fastapi import APIRouter, status

from app.core.database import DbConnection
from app.core.errors import documentar_erro
from .schemas import FeedbackCreate, FeedbackCreated
from .service import FeedbackService

router = APIRouter(prefix="/api/projects", tags=["Feedbacks"])


@router.post(
    "/{project_id}/feedbacks",
    response_model=FeedbackCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Deixar um feedback com nota",
    response_description="O feedback guardado e como ficou a média",
    description=(
        "Mande quem está avaliando, um comentário e uma nota inteira (1 a 5). Em seguida o service guarda "
        "o feedback e refaz a média do projeto com 1 casa decimal antes do commit, então ou os dois "
        "ficam salvos ou nenhum fica. Exemplo: notas 5, 4 e 4 deixam o projeto com média 4.3."
    ),
    responses={
        400: documentar_erro(400, "Os dados enviados são inválidos.", "POST /api/projects/1/feedbacks",
                             {"rating": "O maior valor aceito é 5."}),
        404: documentar_erro(404, "Nenhum projeto tem o id 424242.", "POST /api/projects/424242/feedbacks"),
    },
)
def rate_project(project_id: int, body: FeedbackCreate, db: DbConnection):
    return FeedbackService(db).add(project_id, body)
