from psycopg import Connection

from app.core.errors import NotFoundError
from app.modules.projects.repository import ProjectRepository
from .repository import FeedbackRepository
from .schemas import FeedbackCreate, FeedbackCreated, FeedbackResponse


def _average_one_decimal(points: int, count: int) -> float:
    # média em décimos, arredondando meio para cima só com inteiros: 4.25 vira 4.3 e 4.24 vira 4.2
    tenths = (points * 20 + count) // (count * 2)
    return tenths / 10


class FeedbackService:
    def __init__(self, db: Connection):
        self.repo = FeedbackRepository(db)
        self.projects = ProjectRepository(db)

    def add(self, project_id: int, data: FeedbackCreate) -> FeedbackCreated:
        # FOR UPDATE: se duas pessoas avaliarem o mesmo projeto juntas, a segunda espera a primeira terminar
        if self.projects.lock(project_id) is None:
            raise NotFoundError(f"Nenhum projeto tem o id {project_id}.")

        row = self.repo.insert(project_id, data.author_name, data.comment, data.rating)
        by_rating = self.repo.count_by_rating(project_id)
        count = sum(r["quantity"] for r in by_rating)
        points = sum(r["rating"] * r["quantity"] for r in by_rating)
        average = _average_one_decimal(points, count)
        self.projects.save_average(project_id, average)  # o commit sai junto com o do feedback

        return FeedbackCreated(
            project_id=project_id,
            feedback=FeedbackResponse(**row),
            average_rating=average,
            ratings_count=count,
        )
