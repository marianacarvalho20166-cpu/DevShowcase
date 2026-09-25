"""Conexão com o PostgreSQL (psycopg 3, SQL escrito à mão) e criação das tabelas."""
import os
from typing import Annotated, Iterator

import psycopg
from dotenv import load_dotenv
from fastapi import Depends
from psycopg.rows import dict_row

load_dotenv()  # na máquina de quem desenvolve, carrega o .env; no Render a DATABASE_URL já vem do painel


def _read_database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "Falta a DATABASE_URL: sem ela a API não sabe em qual PostgreSQL entrar. "
            "Na sua máquina, duplique o .env.example, renomeie a cópia para .env e preencha usuário, senha e banco; "
            "no Render, cadastre a DATABASE_URL em Environment."
        )
    # aceita URLs no formato do SQLAlchemy (postgresql+psycopg://...) tirando o "+driver"
    scheme, sep, rest = url.partition("://")
    return scheme.split("+")[0] + sep + rest


DATABASE_URL = _read_database_url()

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name    TEXT         NOT NULL,
    email        TEXT         NOT NULL,
    headline     TEXT,
    github_url   TEXT,
    linkedin_url TEXT,
    created_at   TIMESTAMP(0) NOT NULL DEFAULT now()
);
-- Ana@email.com e ana@email.com contam como o mesmo e-mail
CREATE UNIQUE INDEX IF NOT EXISTS perfil_email_sem_repeticao ON profiles (LOWER(email));

CREATE TABLE IF NOT EXISTS technologies (
    id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name     TEXT NOT NULL,
    category TEXT
);
-- idem para tecnologias: Python e PYTHON não podem existir ao mesmo tempo
CREATE UNIQUE INDEX IF NOT EXISTS tecnologia_nome_sem_repeticao ON technologies (LOWER(name));

-- Profile 1:N Project
CREATE TABLE IF NOT EXISTS projects (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_id     INTEGER      NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title          TEXT         NOT NULL,
    summary        TEXT,
    repo_url       TEXT         NOT NULL,
    live_url       TEXT,
    stars          INTEGER      NOT NULL DEFAULT 0,
    average_rating NUMERIC(2,1),  -- NULL enquanto ninguém avaliou (não é o mesmo que nota zero)
    created_at     TIMESTAMP(0) NOT NULL DEFAULT now()
);

-- Project N:N Technology (tabela associativa)
CREATE TABLE IF NOT EXISTS project_technologies (
    project_id    INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    technology_id INTEGER NOT NULL REFERENCES technologies(id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, technology_id)
);

-- Project 1:N Feedback
CREATE TABLE IF NOT EXISTS feedbacks (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id  INTEGER      NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    author_name TEXT         NOT NULL,
    comment     TEXT         NOT NULL,
    rating      INTEGER      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    created_at  TIMESTAMP(0) NOT NULL DEFAULT now()
);
"""


def connect() -> psycopg.Connection:
    # dict_row: cada linha vem como dicionário {coluna: valor}
    # TimeZone: o created_at sai no horário de Brasília (o PostgreSQL do Render usa UTC)
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=10,
                           options="-c TimeZone=America/Sao_Paulo")


def init_db() -> None:
    """Cria as tabelas se ainda não existirem (o banco novo do Render começa vazio)."""
    try:
        with connect() as conn:
            conn.execute(SCHEMA)
    except psycopg.OperationalError as exc:
        raise RuntimeError(f"Não foi possível conectar ao PostgreSQL pela DATABASE_URL: {exc}") from exc


def get_db() -> Iterator[psycopg.Connection]:
    """Dependência do FastAPI: uma conexão por requisição, commit no fim e rollback se der erro."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# scope="function": o commit acontece antes de a resposta sair para o cliente
DbConnection = Annotated[psycopg.Connection, Depends(get_db, scope="function")]
