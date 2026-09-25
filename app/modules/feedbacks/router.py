from fastapi import APIRouter, status

from app.core.database import DbConnection
from app.core.errors import doc_erro
from .schemas import FeedbackCreate, FeedbackCreated
from .service import FeedbackService

router = APIRouter(prefix="/api/projects", tags=["Feedbacks"])


@router.post(
    "/{project_id}/feedbacks",
    response_model=FeedbackCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Avaliar projeto (nota de 1 a 5)",
    response_description="Feedback salvo e nova média",
    description=(
        "Salva o feedback e recalcula a nota média do projeto (1 casa decimal) na mesma transação. "
        "Exemplo: notas 5 e 3 deixam a média em 4.0."
    ),
    responses={
        400: doc_erro(400, "Os dados enviados são inválidos.", "POST /api/projects/1/feedbacks",
                      {"rating": "Deve ser no máximo 5."}),
        404: doc_erro(404, "Projeto 999 não encontrado.", "POST /api/projects/999/feedbacks"),
    },
)
def create_feedback(project_id: int, body: FeedbackCreate, db: DbConnection):
    return FeedbackService(db).create(project_id, body)
