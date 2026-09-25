from typing import Optional

from psycopg import Connection


class TechnologyRepository:
    def __init__(self, db: Connection):
        self.db = db

    def insert(self, name: str, category: Optional[str]) -> int:
        row = self.db.execute(
            "INSERT INTO technologies (name, category) VALUES (%s, %s) RETURNING id", (name, category)
        ).fetchone()
        return row["id"]

    def find_by_id(self, tech_id: int) -> Optional[dict]:
        return self.db.execute("SELECT * FROM technologies WHERE id = %s", (tech_id,)).fetchone()

    def find_by_name(self, name: str) -> Optional[dict]:
        return self.db.execute(
            "SELECT * FROM technologies WHERE LOWER(name) = LOWER(%s)", (name,)
        ).fetchone()

    def find_all(self) -> list[dict]:
        return self.db.execute("SELECT * FROM technologies ORDER BY name").fetchall()

    def find_existing_ids(self, ids: list[int]) -> set[int]:
        if not ids:
            return set()
        rows = self.db.execute("SELECT id FROM technologies WHERE id = ANY(%s)", (ids,)).fetchall()
        return {r["id"] for r in rows}

    def find_by_project(self, project_id: int) -> list[dict]:
        return self.db.execute(
            """SELECT t.* FROM technologies t
               JOIN project_technologies pt ON pt.technology_id = t.id
               WHERE pt.project_id = %s ORDER BY t.name""",
            (project_id,),
        ).fetchall()
