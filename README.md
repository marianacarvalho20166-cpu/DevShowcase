# DevShowcase API — Grupo 4

API REST de uma vitrine de projetos de desenvolvedores, feita em **Python 3.10+ com FastAPI** e banco **SQLite** acessado pelo módulo `sqlite3` nativo do Python (consultas SQL escritas à mão nos repositórios, sem ORM).

**Integrantes:** Elismar Francelina de Carvalho · Mariana Gomes Carvalho · Kaenny Ribeiro Granja

## Modelo de domínio

| Entidade | Relacionamentos |
|---|---|
| **Profile** (perfil do desenvolvedor) | 1:N com Project |
| **Project** (projeto do portfólio) | N:1 com Profile · N:N com Technology · 1:N com Feedback |
| **Technology** (linguagem, framework, banco…) | N:N com Project, pela tabela `project_technologies` |
| **Feedback** (comentário e nota de 1 a 5) | N:1 com Project |

## Organização do código

Cada entidade tem seu próprio módulo com quatro camadas:

```
app/
├── main.py                  # cria a aplicação e registra as rotas
├── core/
│   ├── database.py          # conexão SQLite e criação das tabelas
│   ├── errors.py            # erros de negócio e respostas de erro padronizadas
│   └── types.py             # tipos de texto validados usados nos DTOs
└── modules/
    ├── profiles/            # schemas.py (DTOs) · repository.py · service.py · router.py
    ├── technologies/
    ├── projects/
    └── feedbacks/           # entidade e repositório (endpoints na próxima etapa)
postman/
└── DevShowcase-Grupo4.postman_collection.json
```

- **schemas.py**: DTOs de entrada (com validação) e de saída.
- **repository.py**: acesso ao banco com SQL.
- **service.py**: regras de negócio (e-mail único, tecnologia sem repetição, perfil e tecnologias precisam existir).
- **router.py**: os endpoints HTTP.

## Como executar

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000` e a documentação automática fica em `http://127.0.0.1:8000/docs`. O arquivo `devshowcase.db` é criado sozinho na primeira execução; para começar do zero, basta apagá-lo com a API parada.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/profiles` | Cadastra um perfil |
| GET | `/api/profiles/{id}` | Busca um perfil com seus projetos |
| POST | `/api/technologies` | Cadastra uma tecnologia |
| GET | `/api/technologies` | Lista as tecnologias |
| POST | `/api/projects` | Cadastra um projeto ligado a um perfil e a tecnologias |
| GET | `/api/projects` | Lista os projetos com dono, tecnologias e feedbacks |

### Exemplo: cadastrar projeto

```json
{
  "profile_id": 1,
  "title": "Agenda Escolar",
  "summary": "API para organizar tarefas e provas da turma",
  "repo_url": "https://github.com/marianagomes/agenda-escolar",
  "technology_ids": [1, 2, 3]
}
```

## Validações

- Nomes e títulos não podem ser vazios (espaços em branco também são recusados).
- URLs (`repo_url`, `live_url`, `github_url`, `linkedin_url`) precisam ser válidas.
- E-mail precisa ser válido e não pode se repetir.
- Tecnologia não pode ser cadastrada duas vezes (sem diferenciar maiúsculas).
- Projeto só é criado se o perfil e todas as tecnologias informadas existirem.

Respostas de erro seguem sempre o mesmo formato:

```json
{ "status": 422, "erro": "Os dados enviados são inválidos.", "campos": { "title": "Não pode ficar vazio." } }
```

## Testando no Postman

Importe `postman/DevShowcase-Grupo4.postman_collection.json` e rode as requisições na ordem das pastas: **1 - Tecnologias → 2 - Perfis → 3 - Projetos**. Os casos de erro ficam no fim de cada pasta.
