from typing import Optional

from psycopg import Connection


class ProfileRepository:
    def __init__(self, db: Connection):
        self.db = db

    def insert(self, full_name, email, headline, github_url, linkedin_url) -> int:
        row = self.db.execute(
            """INSERT INTO profiles (full_name, email, headline, github_url, linkedin_url)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (full_name, email, headline, github_url, linkedin_url),
        ).fetchone()
        return row["id"]

    def find_by_id(self, profile_id: int) -> Optional[dict]:
        return self.db.execute("SELECT * FROM profiles WHERE id = %s", (profile_id,)).fetchone()

    def find_by_email(self, email: str) -> Optional[dict]:
        return self.db.execute(
            "SELECT id FROM profiles WHERE LOWER(email) = LOWER(%s)", (email,)
        ).fetchone()

    def find_projects(self, profile_id: int) -> list[dict]:
        return self.db.execute(
            "SELECT id, title, repo_url FROM projects WHERE profile_id = %s ORDER BY id",
            (profile_id,),
        ).fetchall()
