import sqlite3

from app.core.errors import BusinessError, NotFoundError
from app.modules.feedbacks.repository import FeedbackRepository
from app.modules.feedbacks.schemas import FeedbackResponse
from app.modules.profiles.repository import ProfileRepository
from app.modules.technologies.repository import TechnologyRepository
from app.modules.technologies.schemas import TechnologyResponse
from .repository import ProjectRepository
from .schemas import ProjectCreate, ProjectOwner, ProjectResponse


def _url(value):
    return str(value) if value else None


class ProjectService:
    def __init__(self, db: sqlite3.Connection):
        self.repo = ProjectRepository(db)
        self.profiles = ProfileRepository(db)
        self.technologies = TechnologyRepository(db)
        self.feedbacks = FeedbackRepository(db)

    def create(self, data: ProjectCreate) -> ProjectResponse:
        if self.profiles.find_by_id(data.profile_id) is None:
            raise NotFoundError(f"Perfil {data.profile_id} não encontrado.")

        missing = set(data.technology_ids) - self.technologies.find_existing_ids(data.technology_ids)
        if missing:
            raise BusinessError(f"Tecnologias inexistentes: {sorted(missing)}.")

        project_id = self.repo.insert(
            data.profile_id, data.title, data.summary,
            _url(data.repo_url), _url(data.live_url),
        )
        self.repo.link_technologies(project_id, data.technology_ids)
        return self._to_response(self.repo.find_by_id(project_id))

    def list_all(self) -> list[ProjectResponse]:
        return [self._to_response(row) for row in self.repo.find_all()]

    def _to_response(self, row: sqlite3.Row) -> ProjectResponse:
        techs = [TechnologyResponse(**dict(t)) for t in self.technologies.find_by_project(row["id"])]
        feedbacks = [
            FeedbackResponse(**{k: f[k] for k in f.keys() if k != "project_id"})
            for f in self.feedbacks.find_by_project(row["id"])
        ]
        average = round(sum(f.rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else None
        return ProjectResponse(
            id=row["id"],
            title=row["title"],
            summary=row["summary"],
            repo_url=row["repo_url"],
            live_url=row["live_url"],
            created_at=row["created_at"],
            owner=ProjectOwner(id=row["profile_id"], full_name=row["owner_name"]),
            technologies=techs,
            feedbacks=feedbacks,
            average_rating=average,
        )
