from decimal import ROUND_HALF_UP, Decimal

from psycopg import Connection

from app.core.errors import NotFoundError
from app.modules.projects.repository import ProjectRepository
from .repository import FeedbackRepository
from .schemas import FeedbackCreate, FeedbackCreated, FeedbackResponse


class FeedbackService:
    def __init__(self, db: Connection):
        self.repo = FeedbackRepository(db)
        self.projects = ProjectRepository(db)

    def create(self, project_id: int, data: FeedbackCreate) -> FeedbackCreated:
        # trava a linha do projeto até o commit: dois feedbacks ao mesmo tempo não perdem a média
        if self.projects.lock(project_id) is None:
            raise NotFoundError(f"Projeto {project_id} não encontrado.")

        row = self.repo.insert(project_id, data.author_name, data.comment, data.rating)
        stats = self.repo.rating_stats(project_id)
        average = Decimal(stats["average"]).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        self.projects.update_average(project_id, average)

        return FeedbackCreated(
            project_id=project_id,
            feedback=FeedbackResponse(**row),
            average_rating=float(average),
            ratings_count=stats["total"],
        )
