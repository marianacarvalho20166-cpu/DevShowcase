from psycopg import Connection

from app.core.errors import ConflictError, NotFoundError
from .repository import ProfileRepository
from .schemas import ProfileCreate, ProfileResponse, ProjectSummary


def _url(value):
    return str(value) if value else None


class ProfileService:
    def __init__(self, db: Connection):
        self.repo = ProfileRepository(db)

    def create(self, data: ProfileCreate) -> ProfileResponse:
        if self.repo.find_by_email(data.email):
            raise ConflictError("Já existe um perfil com esse e-mail.")
        new_id = self.repo.insert(
            data.full_name, data.email, data.headline,
            _url(data.github_url), _url(data.linkedin_url),
        )
        return self.get(new_id)

    def get(self, profile_id: int) -> ProfileResponse:
        row = self.repo.find_by_id(profile_id)
        if row is None:
            raise NotFoundError(f"Perfil {profile_id} não encontrado.")
        projects = [ProjectSummary(**p) for p in self.repo.find_projects(profile_id)]
        return ProfileResponse(**row, total_projects=len(projects), projects=projects)
