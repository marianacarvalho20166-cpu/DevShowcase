from psycopg import Connection

from app.core.errors import ConflictError
from .repository import TechnologyRepository
from .schemas import TechnologyCreate, TechnologyResponse


class TechnologyService:
    def __init__(self, db: Connection):
        self.repo = TechnologyRepository(db)

    def create(self, data: TechnologyCreate) -> TechnologyResponse:
        if self.repo.find_by_name(data.name):
            raise ConflictError(f"A tecnologia '{data.name}' já está cadastrada.")
        new_id = self.repo.insert(data.name, data.category)
        return TechnologyResponse(**self.repo.find_by_id(new_id))

    def list_all(self) -> list[TechnologyResponse]:
        return [TechnologyResponse(**r) for r in self.repo.find_all()]
