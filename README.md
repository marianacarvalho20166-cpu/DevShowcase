# DevShowcase API — Grupo 4

API REST de uma vitrine de projetos de desenvolvedores, feita em **Python 3.12 com FastAPI** e banco **PostgreSQL** acessado com o **psycopg 3** (consultas SQL escritas à mão nos repositórios, sem ORM).

**Integrantes:** Elismar Francelina de Carvalho · Mariana Gomes Carvalho · Kaenny Ribeiro Granja

**API em produção:** `https://URL-DO-RENDER.onrender.com` *(preencher depois do deploy)*
**Documentação (Swagger):** `https://URL-DO-RENDER.onrender.com/docs`

## Tecnologias

| Uso | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | FastAPI + Uvicorn |
| Validação dos DTOs | Pydantic 2 |
| Banco de dados | PostgreSQL |
| Acesso ao banco | psycopg 3 (SQL puro, sem ORM) |
| Configuração | python-dotenv (`DATABASE_URL` no `.env`) |
| Testes da API | Postman |
| Hospedagem | Render |

## Modelo de domínio

| Entidade | Relacionamentos |
|---|---|
| **Profile** (perfil do desenvolvedor) | 1:N com Project |
| **Project** (projeto do portfólio, com estrelas e nota média) | N:1 com Profile · N:N com Technology · 1:N com Feedback |
| **Technology** (linguagem, framework, banco…) | N:N com Project, pela tabela `project_technologies` |
| **Feedback** (comentário e nota de 1 a 5) | N:1 com Project |

## Organização do código

Cada entidade tem seu próprio módulo com quatro camadas:

```
app/
├── main.py                  # cria a aplicação, a documentação e registra as rotas
├── core/
│   ├── database.py          # conexão PostgreSQL (DATABASE_URL) e criação das tabelas
│   ├── errors.py            # erros de negócio e manipulador global de erros
│   └── types.py             # tipos de texto validados usados nos DTOs
└── modules/
    ├── profiles/            # schemas.py (DTOs) · repository.py · service.py · router.py
    ├── technologies/
    ├── projects/            # cadastro, listagem com filtro/paginação e upvote
    └── feedbacks/           # feedbacks e cálculo da nota média
postman/
└── DevShowcase-Grupo4.postman_collection.json
```

- **schemas.py**: DTOs de entrada (com validação) e de saída.
- **repository.py**: acesso ao banco com SQL.
- **service.py**: regras de negócio (e-mail único, tecnologia sem repetição, perfil e tecnologias precisam existir, cálculo da média).
- **router.py**: os endpoints HTTP.

## Como executar localmente

Pré-requisitos: Python 3.12 e um PostgreSQL rodando na máquina.

1. Crie um banco vazio (pelo pgAdmin ou pelo terminal):

   ```bash
   psql -U postgres -c "CREATE DATABASE devshowcase;"
   ```

2. Copie o `.env.example` para `.env` e coloque a URL do seu banco:

   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/devshowcase
   ```

   O `.env` está no `.gitignore` e nunca vai para o GitHub.

3. Instale as dependências e suba a API:

   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate

   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

A API sobe em `http://127.0.0.1:8000`. As tabelas são criadas sozinhas na primeira execução. Se a `DATABASE_URL` não estiver definida, a API não inicia e mostra a mensagem *"A variável de ambiente DATABASE_URL não foi definida..."*.

## Documentação interativa

- **Swagger:** `http://127.0.0.1:8000/docs` (a rota `/` redireciona para lá)
- **OpenAPI (JSON):** `http://127.0.0.1:8000/openapi.json`

Cada rota tem resumo, exemplo de corpo e as respostas de erro documentadas.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/technologies` | Cadastra uma tecnologia |
| GET | `/api/technologies` | Lista as tecnologias |
| POST | `/api/profiles` | Cadastra um perfil |
| GET | `/api/profiles/{id}` | Busca um perfil com seus projetos |
| POST | `/api/projects` | Cadastra um projeto ligado a um perfil e a tecnologias |
| GET | `/api/projects` | Lista os projetos com filtro por tecnologia e paginação |
| PUT | `/api/projects/{id}/upvote` | Dá uma estrela ao projeto |
| POST | `/api/projects/{id}/feedbacks` | Cadastra um feedback e recalcula a nota média |
| GET | `/health` | Confere se a API está no ar |

### Listar projetos com filtro e paginação

`GET /api/projects?tech=python&page=1&per_page=5`

| Parâmetro | Padrão | Regra |
|---|---|---|
| `tech` | — | nome da tecnologia, sem diferenciar maiúsculas (`python`, `PYTHON`, `Python`) |
| `page` | 1 | número inteiro a partir de 1 |
| `per_page` | 5 | número inteiro de 1 a 20 |

Resposta `200`:

```json
{
  "total": 7,
  "page": 1,
  "per_page": 5,
  "total_pages": 2,
  "results": [
    {
      "id": 7,
      "title": "Agenda Escolar",
      "summary": "API para organizar tarefas e provas da turma",
      "repo_url": "https://github.com/marianagomes/agenda-escolar",
      "live_url": null,
      "stars": 0,
      "average_rating": null,
      "created_at": "2026-09-25T15:57:48",
      "owner": { "id": 3, "full_name": "Mariana Gomes Carvalho" },
      "technologies": [
        { "id": 2, "name": "FastAPI", "category": "Framework" },
        { "id": 3, "name": "PostgreSQL", "category": "Banco de dados" },
        { "id": 1, "name": "Python", "category": "Linguagem" }
      ],
      "feedbacks": []
    }
  ]
}
```

Os projetos vêm do mais novo para o mais antigo. Uma página além do fim (ex.: `page=99`) responde `200` com `"results": []`. Página `0`, `per_page` acima de 20 ou texto no lugar de número respondem `400`.

### Dar estrela (upvote)

`PUT /api/projects/1/upvote` (sem corpo). O banco soma a estrela de forma atômica (`SET stars = stars + 1`), então cliques ao mesmo tempo não se perdem.

Resposta `200`: o projeto atualizado, no mesmo formato da listagem, com `"stars"` somado (aqui era 2 e foi para 3):

```json
{
  "id": 1,
  "title": "Cardápio Digital",
  "summary": "Cardápio online de lanchonete com pedidos pelo celular",
  "repo_url": "https://github.com/elismarcarvalho/cardapio-digital",
  "live_url": null,
  "stars": 3,
  "average_rating": null,
  "created_at": "2026-09-25T15:57:47",
  "owner": { "id": 1, "full_name": "Elismar Francelina de Carvalho" },
  "technologies": [
    { "id": 2, "name": "FastAPI", "category": "Framework" },
    { "id": 3, "name": "PostgreSQL", "category": "Banco de dados" },
    { "id": 1, "name": "Python", "category": "Linguagem" }
  ],
  "feedbacks": []
}
```

Projeto inexistente responde `404`.

### Cadastrar feedback

`POST /api/projects/2/feedbacks`

```json
{
  "author_name": "Elismar Francelina de Carvalho",
  "comment": "Funciona bem, mas faltou um relatório de mensalidades.",
  "rating": 3
}
```

Resposta `201` (o projeto já tinha uma nota 5, então a média foi para 4):

```json
{
  "project_id": 2,
  "feedback": {
    "id": 2,
    "author_name": "Elismar Francelina de Carvalho",
    "comment": "Funciona bem, mas faltou um relatório de mensalidades.",
    "rating": 3,
    "created_at": "2026-09-25T15:57:49"
  },
  "average_rating": 4.0,
  "ratings_count": 2
}
```

O service salva o feedback, calcula a média com `AVG` no banco, arredonda para 1 casa decimal e grava em `projects.average_rating`, tudo na **mesma transação**. Se algo falhar no meio, nada é salvo.

### Cadastrar projeto (etapa 1)

```json
{
  "profile_id": 1,
  "title": "Cardápio Digital",
  "summary": "Cardápio online de lanchonete com pedidos pelo celular",
  "repo_url": "https://github.com/elismarcarvalho/cardapio-digital",
  "technology_ids": [1, 2, 3]
}
```

## Validações

- Nomes, títulos e comentários não podem ser vazios (espaços em branco também são recusados).
- URLs (`repo_url`, `live_url`, `github_url`, `linkedin_url`) precisam ser válidas.
- E-mail precisa ser válido e não pode se repetir (sem diferenciar maiúsculas).
- Tecnologia não pode ser cadastrada duas vezes (sem diferenciar maiúsculas).
- Projeto só é criado se o perfil e todas as tecnologias informadas existirem.
- Nota do feedback: número inteiro de 1 a 5 (`true`, `"4"` e `4.0` são recusados, sem conversão).
- Textos não podem conter o caractere nulo (`\u0000`), que o PostgreSQL não aceita.

## Formato de erro

Todos os erros passam pelo manipulador global em `app/core/errors.py` e saem no mesmo formato:

```json
{
  "status": 400,
  "erro": "Os dados enviados são inválidos.",
  "campos": { "rating": "Deve ser no máximo 5.", "comment": "Não pode ficar vazio." },
  "rota": "POST /api/projects/2/feedbacks"
}
```

| Código | Quando acontece |
|---|---|
| 400 | Campo inválido, parâmetro de página inválido, id da rota que não é número, JSON malformado ou enviado sem `Content-Type: application/json`, texto com o caractere nulo (`\u0000`), tecnologia inexistente no cadastro de projeto |
| 404 | Perfil ou projeto inexistente, ou rota que não existe |
| 405 | Método HTTP errado para a rota |
| 409 | E-mail ou tecnologia repetidos |
| 500 | Erro inesperado (a resposta não mostra detalhes internos; eles ficam só no log) |
| 503 | Banco de dados fora do ar ou inacessível (a API responde, mas não consegue falar com o PostgreSQL) |

Outros exemplos:

```json
{ "status": 400, "erro": "O corpo da requisição não é um JSON válido.", "campos": { "body": "JSON malformado: confira aspas, vírgulas e chaves." }, "rota": "POST /api/projects/2/feedbacks" }
```

```json
{ "status": 404, "erro": "Projeto 999999 não encontrado.", "rota": "PUT /api/projects/999999/upvote" }
```

## Testando no Postman

Importe `postman/DevShowcase-Grupo4.postman_collection.json`. A variável da coleção `baseUrl` vem com `http://localhost:8000`; para testar em produção, troque pela URL do Render.

Rode as pastas na ordem:

1. **0 - Popular banco**: cadastra tecnologias, perfis e projetos e guarda os ids em variáveis. Pode ser rodada de novo (tecnologia repetida aceita 409 e os e-mails usam `{{$timestamp}}`).
2. **1 - Tecnologias**, **2 - Perfis**, **3 - Projetos**: endpoints da etapa 1.
3. **4 - Listagem com filtro e páginas**, **5 - Estrelas (upvote)**, **6 - Feedbacks e média**: endpoints da etapa 2.

Os casos de erro ficam no fim de cada pasta, e toda requisição tem testes conferindo o status esperado.

Dá para clicar **Send** de novo em qualquer requisição ou rodar de novo só uma pasta sem os testes ficarem vermelhos: estrelas, médias e totais são conferidos em relação ao valor de antes da requisição. As pastas **5** e **6** têm um *Pre-request* que guarda as estrelas do Cardápio Digital e as notas do Controle de Academia antes de cada envio (se os ids ainda estiverem vazios, usa o projeto mais novo com esse título).

## Deploy no Render

1. **Banco:** no painel do Render, clique em **New > Postgres**. Dê um nome (ex.: `devshowcase-db`), escolha a região, o plano **Free** e clique em **Create Database**.
2. Quando o banco ficar disponível, copie a **Internal Database URL** (na página do banco, em *Connections*).
3. **API:** clique em **New > Web Service** e conecte este repositório do GitHub. Preencha:
   - **Language:** Python 3 (a versão 3.12 vem do arquivo `.python-version`)
   - **Branch:** `main`
   - **Region:** a **mesma** do banco
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
4. Em **Environment Variables**, adicione `DATABASE_URL` com a Internal Database URL copiada no passo 2.
5. Em **Advanced**, deixe **Auto-Deploy** em **On Commit** (cada push na `main` publica de novo) e, se quiser, coloque `/health` em **Health Check Path**.
6. Clique em **Create Web Service** e espere aparecer *Your service is live*. As tabelas são criadas na primeira inicialização.
7. Abra `https://URL-DO-RENDER.onrender.com/docs`, troque o `baseUrl` do Postman para essa URL e rode a pasta **0 - Popular banco**.

Observações sobre o plano Free do Render:

- A API "dorme" depois de 15 minutos sem uso. A primeira requisição depois disso acorda o serviço e pode levar cerca de um minuto; abra o `/docs` antes de gravar o vídeo.
- O PostgreSQL Free expira 30 dias depois de criado. Depois disso é preciso criar um banco novo, trocar a `DATABASE_URL` do Web Service e rodar de novo a pasta **0 - Popular banco** do Postman.
