from decimal import Decimal
from typing import Optional

from psycopg import Connection

# Projetos que usam a tecnologia informada (sem diferenciar maiúsculas)
TECH_FILTER = """ WHERE EXISTS (
        SELECT 1 FROM project_technologies pt
        JOIN technologies t ON t.id = pt.technology_id
        WHERE pt.project_id = p.id AND LOWER(t.name) = LOWER(%s))"""


class ProjectRepository:
    def __init__(self, db: Connection):
        self.db = db

    def insert(self, profile_id, title, summary, repo_url, live_url) -> int:
        row = self.db.execute(
            """INSERT INTO projects (profile_id, title, summary, repo_url, live_url)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (profile_id, title, summary, repo_url, live_url),
        ).fetchone()
        return row["id"]

    def link_technologies(self, project_id: int, technology_ids: list[int]) -> None:
        with self.db.cursor() as cur:
            cur.executemany(
                """INSERT INTO project_technologies (project_id, technology_id) VALUES (%s, %s)
                   ON CONFLICT DO NOTHING""",
                [(project_id, t) for t in technology_ids],
            )

    def _select(self) -> str:
        return """SELECT p.*, pr.full_name AS owner_name
                  FROM projects p JOIN profiles pr ON pr.id = p.profile_id"""

    def find_by_id(self, project_id: int) -> Optional[dict]:
        return self.db.execute(self._select() + " WHERE p.id = %s", (project_id,)).fetchone()

    def count(self, tech: Optional[str]) -> int:
        sql, params = "SELECT COUNT(*) AS total FROM projects p", ()
        if tech:
            sql, params = sql + TECH_FILTER, (tech,)
        return self.db.execute(sql, params).fetchone()["total"]

    def find_page(self, tech: Optional[str], limit: int, offset: int) -> list[dict]:
        sql, params = self._select(), ()
        if tech:
            sql, params = sql + TECH_FILTER, (tech,)
        return self.db.execute(
            sql + " ORDER BY p.id DESC LIMIT %s OFFSET %s", (*params, limit, offset)
        ).fetchall()

    def add_star(self, project_id: int) -> Optional[dict]:
        # incremento atômico: o próprio banco soma, sem ler o valor antes
        return self.db.execute(
            "UPDATE projects SET stars = stars + 1 WHERE id = %s RETURNING id", (project_id,)
        ).fetchone()

    def lock(self, project_id: int) -> Optional[dict]:
        return self.db.execute(
            "SELECT id FROM projects WHERE id = %s FOR UPDATE", (project_id,)
        ).fetchone()

    def update_average(self, project_id: int, average: Decimal) -> None:
        self.db.execute(
            "UPDATE projects SET average_rating = %s WHERE id = %s", (average, project_id)
        )
