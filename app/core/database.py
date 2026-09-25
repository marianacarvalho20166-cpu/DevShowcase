"""Conexão com o SQLite (módulo sqlite3 nativo do Python) e criação das tabelas."""
import sqlite3
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).resolve().parents[2] / "devshowcase.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name    TEXT    NOT NULL,
    email        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    headline     TEXT,
    github_url   TEXT,
    linkedin_url TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS technologies (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL UNIQUE COLLATE NOCASE,
    category TEXT
);

-- Profile 1:N Project
CREATE TABLE IF NOT EXISTS projects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title      TEXT    NOT NULL,
    summary    TEXT,
    repo_url   TEXT    NOT NULL,
    live_url   TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Project N:N Technology (tabela associativa)
CREATE TABLE IF NOT EXISTS project_technologies (
    project_id    INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    technology_id INTEGER NOT NULL REFERENCES technologies(id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, technology_id)
);

-- Project 1:N Feedback
CREATE TABLE IF NOT EXISTS feedbacks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    author_name TEXT    NOT NULL,
    comment     TEXT    NOT NULL,
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row          # linhas acessíveis por nome de coluna
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite só respeita FK com isso ligado
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependência do FastAPI: abre uma conexão por requisição e fecha no final."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
