import sqlite3


class FeedbackRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def insert(self, project_id: int, author_name: str, comment: str, rating: int) -> int:
        cur = self.db.execute(
            "INSERT INTO feedbacks (project_id, author_name, comment, rating) VALUES (?, ?, ?, ?)",
            (project_id, author_name, comment, rating),
        )
        return cur.lastrowid

    def find_by_project(self, project_id: int) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT * FROM feedbacks WHERE project_id = ? ORDER BY created_at DESC", (project_id,)
        ).fetchall()
