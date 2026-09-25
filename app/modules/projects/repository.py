from typing import Optional

from psycopg import Connection

# Só os projetos ligados à tecnologia pedida (o nome é comparado sem ligar para maiúsculas)
FILTRO_TECNOLOGIA = """ WHERE p.id IN (
        SELECT vinculo.project_id
        FROM project_technologies vinculo
        JOIN technologies tec ON tec.id = vinculo.technology_id
        WHERE LOWER(tec.name) = LOWER(%s))"""


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

    def count_matching(self, tech: Optional[str]) -> int:
        sql, params = "SELECT COUNT(*) AS total FROM projects p", ()
        if tech:
            sql, params = sql + FILTRO_TECNOLOGIA, (tech,)
        return self.db.execute(sql, params).fetchone()["total"]

    def fetch_slice(self, tech: Optional[str], limit: int, offset: int) -> list[dict]:
        sql, params = self._select(), ()
        if tech:
            sql, params = sql + FILTRO_TECNOLOGIA, (tech,)
        # mais recentes primeiro; o id desempata projetos criados no mesmo segundo
        return self.db.execute(
            sql + " ORDER BY p.created_at DESC, p.id DESC LIMIT %s OFFSET %s", (*params, limit, offset)
        ).fetchall()

    def add_star(self, project_id: int) -> Optional[dict]:
        # o banco soma direto no UPDATE: dois cliques ao mesmo tempo viram +2, nenhum se perde
        return self.db.execute(
            "UPDATE projects SET stars = stars + 1 WHERE id = %s RETURNING id", (project_id,)
        ).fetchone()

    def lock(self, project_id: int) -> Optional[dict]:
        return self.db.execute(
            "SELECT id FROM projects WHERE id = %s FOR UPDATE", (project_id,)
        ).fetchone()

    def save_average(self, project_id: int, average: float) -> None:
        self.db.execute(
            "UPDATE projects SET average_rating = %s WHERE id = %s", (average, project_id)
        )
