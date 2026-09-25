import sqlite3
from typing import Optional


class TechnologyRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def insert(self, name: str, category: Optional[str]) -> int:
        cur = self.db.execute(
            "INSERT INTO technologies (name, category) VALUES (?, ?)", (name, category)
        )
        return cur.lastrowid

    def find_by_id(self, tech_id: int) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT * FROM technologies WHERE id = ?", (tech_id,)).fetchone()

    def find_by_name(self, name: str) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT * FROM technologies WHERE name = ?", (name,)).fetchone()

    def find_all(self) -> list[sqlite3.Row]:
        return self.db.execute("SELECT * FROM technologies ORDER BY name").fetchall()

    def find_existing_ids(self, ids: list[int]) -> set[int]:
        if not ids:
            return set()
        marks = ",".join("?" * len(ids))
        rows = self.db.execute(f"SELECT id FROM technologies WHERE id IN ({marks})", ids).fetchall()
        return {r["id"] for r in rows}

    def find_by_project(self, project_id: int) -> list[sqlite3.Row]:
        return self.db.execute(
            """SELECT t.* FROM technologies t
               JOIN project_technologies pt ON pt.technology_id = t.id
               WHERE pt.project_id = ? ORDER BY t.name""",
            (project_id,),
        ).fetchall()
