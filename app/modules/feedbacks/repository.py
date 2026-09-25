from psycopg import Connection


class FeedbackRepository:
    def __init__(self, db: Connection):
        self.db = db

    def insert(self, project_id: int, author_name: str, comment: str, rating: int) -> dict:
        return self.db.execute(
            """INSERT INTO feedbacks (project_id, author_name, comment, rating)
               VALUES (%s, %s, %s, %s)
               RETURNING id, author_name, comment, rating, created_at""",
            (project_id, author_name, comment, rating),
        ).fetchone()

    def rating_stats(self, project_id: int) -> dict:
        """Média (AVG) e quantidade de notas do projeto, calculadas pelo banco."""
        return self.db.execute(
            "SELECT AVG(rating) AS average, COUNT(*) AS total FROM feedbacks WHERE project_id = %s",
            (project_id,),
        ).fetchone()

    def find_by_project(self, project_id: int) -> list[dict]:
        return self.db.execute(
            """SELECT id, author_name, comment, rating, created_at FROM feedbacks
               WHERE project_id = %s ORDER BY created_at DESC, id DESC""",
            (project_id,),
        ).fetchall()
