import sqlite3
from typing import Optional


class ProfileRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def insert(self, full_name, email, headline, github_url, linkedin_url) -> int:
        cur = self.db.execute(
            """INSERT INTO profiles (full_name, email, headline, github_url, linkedin_url)
               VALUES (?, ?, ?, ?, ?)""",
            (full_name, email, headline, github_url, linkedin_url),
        )
        return cur.lastrowid

    def find_by_id(self, profile_id: int) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()

    def find_by_email(self, email: str) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT id FROM profiles WHERE email = ?", (email,)).fetchone()

    def find_projects(self, profile_id: int) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT id, title, repo_url FROM projects WHERE profile_id = ? ORDER BY id",
            (profile_id,),
        ).fetchall()
