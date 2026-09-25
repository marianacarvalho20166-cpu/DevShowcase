import sqlite3
from typing import Optional


class ProjectRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def insert(self, profile_id, title, summary, repo_url, live_url) -> int:
        cur = self.db.execute(
            """INSERT INTO projects (profile_id, title, summary, repo_url, live_url)
               VALUES (?, ?, ?, ?, ?)""",
            (profile_id, title, summary, repo_url, live_url),
        )
        return cur.lastrowid

    def link_technologies(self, project_id: int, technology_ids: list[int]) -> None:
        self.db.executemany(
            "INSERT INTO project_technologies (project_id, technology_id) VALUES (?, ?)",
            [(project_id, t) for t in technology_ids],
        )

    def _select(self) -> str:
        return """SELECT p.*, pr.full_name AS owner_name
                  FROM projects p JOIN profiles pr ON pr.id = p.profile_id"""

    def find_by_id(self, project_id: int) -> Optional[sqlite3.Row]:
        return self.db.execute(self._select() + " WHERE p.id = ?", (project_id,)).fetchone()

    def find_all(self) -> list[sqlite3.Row]:
        return self.db.execute(self._select() + " ORDER BY p.id DESC").fetchall()
