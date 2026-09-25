import math
from typing import Optional

from psycopg import Connection

from app.core.errors import BusinessError, NotFoundError
from app.modules.feedbacks.repository import FeedbackRepository
from app.modules.feedbacks.schemas import FeedbackResponse
from app.modules.profiles.repository import ProfileRepository
from app.modules.technologies.repository import TechnologyRepository
from app.modules.technologies.schemas import TechnologyResponse
from .repository import ProjectRepository
from .schemas import ProjectCreate, ProjectListing, ProjectOwner, ProjectResponse


def _url(value):
    return str(value) if value else None


class ProjectService:
    def __init__(self, db: Connection):
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

    def list_filtered(self, tech: Optional[str], page: int, per_page: int) -> ProjectListing:
        total = self.repo.count_matching(tech)
        offset = (page - 1) * per_page
        # pediu uma página depois da última: nem vai ao banco buscar linhas
        rows = self.repo.fetch_slice(tech, per_page, offset) if offset < total else []
        return ProjectListing(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=math.ceil(total / per_page),
            results=[self._to_response(row) for row in rows],
        )

    def give_star(self, project_id: int) -> ProjectResponse:
        if self.repo.add_star(project_id) is None:
            raise NotFoundError(f"Nenhum projeto tem o id {project_id}.")
        return self._to_response(self.repo.find_by_id(project_id))

    def _to_response(self, row: dict) -> ProjectResponse:
        techs = [TechnologyResponse(**t) for t in self.technologies.find_by_project(row["id"])]
        feedbacks = [FeedbackResponse(**f) for f in self.feedbacks.find_by_project(row["id"])]
        average = row["average_rating"]
        return ProjectResponse(
            id=row["id"],
            title=row["title"],
            summary=row["summary"],
            repo_url=row["repo_url"],
            live_url=row["live_url"],
            stars=row["stars"],
            average_rating=float(average) if average is not None else None,
            created_at=row["created_at"],
            owner=ProjectOwner(id=row["profile_id"], full_name=row["owner_name"]),
            technologies=techs,
            feedbacks=feedbacks,
        )
