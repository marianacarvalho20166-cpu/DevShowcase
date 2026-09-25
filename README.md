# DevShowcase API — Grupo 4

Uma vitrine onde cada pessoa desenvolvedora mostra os projetos que fez, conta quais tecnologias usou e recebe estrelas e feedbacks. A API é feita em **Python 3.12 com FastAPI** e guarda tudo num **PostgreSQL**, acessado pelo **psycopg 3** com o SQL escrito por nós nos repositórios (sem ORM).

**Integrantes:** Elismar Francelina de Carvalho · Mariana Gomes Carvalho · Kaenny Ribeiro Granja

## Como testar em 2 minutos

1. Abra o Swagger:
   - **no Render (produção):** https://devshowcase-grupo4.onrender.com/docs — a API fica em https://devshowcase-grupo4.onrender.com;
   - **na sua máquina:** `http://127.0.0.1:8000/docs` (entrar só em `/` também leva para lá).
2. Siga os grupos de rotas na ordem em que aparecem: **Perfis → Tecnologias → Projetos → Feedbacks**. Em cada rota é só clicar em *Try it out*, ajustar o exemplo e clicar em *Execute*.
3. Prefere o Postman? Importe `postman/DevShowcase-Grupo4.postman_collection.json`, confira a variável `baseUrl` e rode a pasta **0 - Montar a vitrine** antes das outras.

### Quais rotas existem?

| Método | Rota | Para que serve | Deu certo |
|---|---|---|---|
| POST | `/api/profiles` | cadastra a pessoa desenvolvedora (nome, e-mail e links) | 201 |
| GET | `/api/profiles/{id}` | traz a pessoa e os projetos que ela publicou | 200 |
| POST | `/api/technologies` | cadastra uma linguagem, framework ou banco | 201 |
| GET | `/api/technologies` | lista as tecnologias, ordenadas pelo nome | 200 |
| POST | `/api/projects` | publica um projeto, dizendo de quem é e quais tecnologias usa | 201 |
| GET | `/api/projects` | lista os projetos; **na etapa 2** ganhou filtro `tech` e páginas | 200 |
| PUT | `/api/projects/{id}/upvote` | **novo:** soma uma estrela ao projeto | 200 |
| POST | `/api/projects/{id}/feedbacks` | **novo:** guarda um feedback com nota e refaz a média | 201 |
| GET | `/health` | responde `{"status": "ok"}` quando a API está de pé | 200 |

## O que tem de novo na etapa 2?

### 1. Como procurar projetos por tecnologia e andar pelas páginas?

`GET /api/projects?tech=fastapi&page=1&per_page=1`

| Parâmetro | Se não mandar | O que aceita |
|---|---|---|
| `tech` | traz todos os projetos | nome da tecnologia: `fastapi`, `FastAPI` e `FASTAPI` trazem os mesmos projetos. Se aparecer na URL, não pode vir vazio |
| `page` | `1` | número inteiro a partir de 1 |
| `per_page` | `5` | número inteiro de 1 a 20 |

Resposta `200`:

```json
{
  "total": 4,
  "page": 1,
  "per_page": 1,
  "total_pages": 4,
  "results": [
    {
      "id": 7,
      "title": "Escola de Música",
      "summary": "Matrículas e horários das aulas de violão e teclado",
      "repo_url": "https://github.com/marianagomes/escola-de-musica",
      "live_url": null,
      "stars": 0,
      "average_rating": null,
      "created_at": "2026-09-25T17:25:10",
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

A ordem segue a data de publicação: quem foi publicado por último aparece primeiro (se dois projetos forem publicados no mesmo segundo, o de id maior vem antes). No SQL, o filtro é um `p.id IN (SELECT ... FROM project_technologies JOIN technologies ...)` que compara os nomes com `LOWER`, e o total vem de um `COUNT(*)` com o mesmo filtro.

Pedir uma página depois da última não é erro: a resposta é `200`, com `results` vazio e os totais preenchidos, assim quem chamou sabe que a lista acabou. Já `per_page=0`, `page=primeira` ou `tech=` (sem valor) voltam `400`.

### 2. Como funciona a estrela (upvote)?

A chamada `PUT /api/projects/8/upvote` vai sem corpo nenhum. Cada uma soma 1 em `stars`, e quem soma é o PostgreSQL, no comando `UPDATE projects SET stars = stars + 1`, sem a API precisar consultar quantas estrelas havia. Por isso, se duas pessoas clicarem juntas na estrela do Pet Shop Agenda, ele ganha duas: nenhuma se perde.

Resposta `200`: o projeto inteiro, já com a estrela contada (aqui é a segunda):

```json
{
  "id": 8,
  "title": "Pet Shop Agenda",
  "summary": "Agenda de banho e tosa com lembrete para o tutor",
  "repo_url": "https://github.com/kaennygranja/pet-shop-agenda",
  "live_url": null,
  "stars": 2,
  "average_rating": null,
  "created_at": "2026-09-25T17:25:05",
  "owner": { "id": 2, "full_name": "Kaenny Ribeiro Granja" },
  "technologies": [],
  "feedbacks": []
}
```

Id que não existe volta `404`; id que não é número (ex.: `/api/projects/xyz/upvote`) volta `400`.

### 3. O que acontece quando alguém deixa um feedback?

`POST /api/projects/9/feedbacks`

```json
{
  "author_name": "Kaenny Ribeiro Granja",
  "comment": "As perguntas são boas, só queria poder ouvir as notas antes de responder.",
  "rating": 3
}
```

Resposta `201` (o Quiz de Teoria Musical já tinha uma nota 5; com esta nota 3 a média foi para 4.0):

```json
{
  "project_id": 9,
  "feedback": {
    "id": 2,
    "author_name": "Kaenny Ribeiro Granja",
    "comment": "As perguntas são boas, só queria poder ouvir as notas antes de responder.",
    "rating": 3,
    "created_at": "2026-09-25T17:25:08"
  },
  "average_rating": 4.0,
  "ratings_count": 2
}
```

Passo a passo dentro do `FeedbackService`:

1. reserva o projeto no banco com `SELECT ... FOR UPDATE` até o commit: quem chegar junto espera a vez, e a média nunca é calculada em cima de notas desatualizadas;
2. guarda o feedback;
3. pergunta ao banco quantas notas de cada valor o projeto tem (por exemplo, duas notas 5 e uma 4) e calcula a média com 1 casa decimal, arredondando o meio para cima (4.25 vira 4.3);
4. grava a média em `projects.average_rating`.

Os quatro passos usam a mesma conexão e só são confirmados no commit do fim da requisição. Se qualquer um falhar, o rollback desfaz tudo e o feedback nunca fica salvo com a média antiga.

A nota tem que ser 1, 2, 3, 4 ou 5, escrita sem aspas: `10`, `"cinco"` e `4.5` voltam `400`. Se o projeto não existir, a resposta é `404`.

## E quando dá erro?

Não importa se o problema apareceu na validação, numa regra do service ou no banco: o `app/core/errors.py` monta a resposta sempre com as mesmas chaves.

| Chave | Quando aparece |
|---|---|
| `status` | sempre (é o próprio código HTTP) |
| `erro` | sempre: o que aconteceu, em português |
| `rota` | sempre: o método e o caminho que foram chamados |
| `campos` | quando algum dado precisa ser corrigido (um texto para cada campo) |
| `dica` | quando dá para sugerir o que fazer (JSON quebrado, rota que não existe...) |

Nota fora da regra:

```json
{
  "status": 400,
  "erro": "Os dados enviados são inválidos.",
  "rota": "POST /api/projects/9/feedbacks",
  "campos": { "rating": "O maior valor aceito é 5." }
}
```

JSON escrito com aspas simples, do jeito do Python:

```json
{
  "status": 400,
  "erro": "Não deu para entender o JSON enviado.",
  "rota": "POST /api/projects/9/feedbacks",
  "campos": { "json": "A leitura parou perto do caractere 1." },
  "dica": "Em JSON, nomes de campo e textos vão entre aspas duplas."
}
```

Perfil que não existe:

```json
{ "status": 404, "erro": "Perfil 424242 não encontrado.", "rota": "GET /api/profiles/424242" }
```

| Código | O que costuma causar |
|---|---|
| 400 | campo faltando ou fora da regra, nota menor que 1 ou maior que 5, `per_page=0`, id que não é número, JSON quebrado ou enviado sem `Content-Type: application/json`, texto com o caractere `\u0000`, tecnologia inexistente no cadastro de projeto |
| 404 | perfil ou projeto que não existe; rota que não existe (essa vem com `dica`) |
| 405 | método que a rota não aceita, ex.: `DELETE /api/projects` |
| 409 | e-mail ou tecnologia que já estão cadastrados |
| 500 | falha inesperada: quem chamou recebe só uma frase genérica, e o erro completo aparece no terminal do servidor (no Render, na aba *Logs*) |
| 503 | a API respondeu, mas não conseguiu falar com o PostgreSQL |

O FastAPI costuma responder `422` quando a validação falha. Aqui esse caso virou `400`, e o `422` também não aparece no Swagger.

### O que a API recusa?

- Nome, título e comentário vazios (ou só com espaços).
- URL que não começa com `http://` ou `https://` em `repo_url`, `live_url`, `github_url` e `linkedin_url`.
- E-mail inválido ou repetido. Maiúsculas não contam: `Ana@email.com` e `ana@email.com` são o mesmo e-mail.
- Tecnologia repetida, também sem ligar para maiúsculas (`fastapi` e `FastAPI` são a mesma).
- Projeto de um perfil que não existe (404) ou com uma tecnologia que não existe (400).
- Nota que não seja 1, 2, 3, 4 ou 5 (número inteiro, sem aspas).

## Deploy no Render

### Passo 1: o banco (New → Postgres)

| Campo no Render | O que preencher |
|---|---|
| Name | `grupo4-postgres` |
| Region | escolha uma; o passo 2 precisa repetir essa região |
| PostgreSQL Version | pode deixar a que vier marcada |
| Instance Type | Free |

Depois de **Create Database**, o Render leva alguns minutos preparando o banco. Quando ele estiver pronto, copie a **Internal Database URL** na seção *Connections*.

### Passo 2: a API (New → Web Service)

| Campo no Render | O que preencher |
|---|---|
| Source Code | este repositório do GitHub |
| Name | `devshowcase-grupo4` (esse nome vira parte da URL) |
| Region | igual à do banco (a Internal Database URL não funciona entre regiões diferentes) |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |
| Environment Variables | `DATABASE_URL` = a Internal Database URL copiada no passo 1 |
| Health Check Path (em *Advanced*) | `/health` |
| Auto-Deploy (em *Advanced*) | *On Commit*, para cada push na `main` publicar de novo |

### Passo 3: conferir

Clique em **Deploy Web Service** e fique de olho na aba *Logs*. Quando o Render mostrar o serviço como *Live*, o `init_db` já criou as tabelas no banco novo. Abra `https://<nome-do-serviço>.onrender.com/docs` (o nosso é https://devshowcase-grupo4.onrender.com/docs), troque o `baseUrl` do Postman por esse endereço e rode a pasta **0 - Montar a vitrine** para encher o banco.

## Limites do plano grátis

- **A API cochila.** Se ficar 15 minutos sem receber requisição, o Render desliga o serviço grátis. Ele liga sozinho na chamada seguinte, só que essa primeira resposta pode demorar quase um minuto. Na hora de gravar, abra o `/health` primeiro e espere aparecer `{"status": "ok"}`.
- **O banco grátis tem validade.** O PostgreSQL Free vence 30 dias depois de criado. Passou disso? Crie outro banco, cole a nova Internal Database URL na `DATABASE_URL` do Web Service e rode a pasta **0 - Montar a vitrine** outra vez (a API cria as tabelas de novo ao ligar).
- **Um banco grátis por vez.** Cada conta só pode ter um PostgreSQL Free ativo; para criar outro, apague o antigo antes.

## Rodando na sua máquina

Você vai precisar do Python 3.12 e do PostgreSQL instalados (o instalador do PostgreSQL já traz o pgAdmin, se preferir fazer tudo por janela).

1. Crie um banco chamado `devshowcase`. Pelo terminal:

   ```bash
   createdb -U postgres devshowcase
   ```

2. Faça uma cópia do `.env.example` com o nome `.env` e troque usuário e senha pelos do seu PostgreSQL:

   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/devshowcase
   ```

   O `.gitignore` já ignora o `.env`, então a senha nunca sobe para o GitHub.

3. Crie o ambiente virtual, instale as dependências e ligue a API:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # no Windows
   source .venv/bin/activate       # no Linux ou Mac

   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

A API responde em `http://127.0.0.1:8000`. Ao ligar, ela cria as tabelas que faltarem (`CREATE TABLE IF NOT EXISTS`), então o banco vazio do passo 1 já basta. Se o `.env` estiver faltando, a API nem sobe e avisa: *"Falta a DATABASE_URL: sem ela a API não sabe em qual PostgreSQL entrar..."*.

## Por dentro do código: como as pastas se dividem?

| Parte | O que usamos |
|---|---|
| Linguagem | Python 3.12 |
| Web e documentação | FastAPI (Swagger em `/docs`) rodando no Uvicorn |
| Validação dos DTOs | Pydantic 2 |
| Banco de dados | PostgreSQL, com psycopg 3 e SQL puro |
| Configuração | python-dotenv, que lê a `DATABASE_URL` do `.env` |
| Testes manuais da API | Postman |
| Hospedagem | Render (Web Service + PostgreSQL) |

| Entidade | Com quem se liga |
|---|---|
| **Profile**: quem publica | tem vários Projects (1:N) |
| **Project**: o trabalho na vitrine, com `stars` e `average_rating` | pertence a um Profile (N:1), usa várias Technologies (N:N) e recebe vários Feedbacks (1:N) |
| **Technology**: linguagem, framework, banco... | aparece em vários Projects (N:N, pela tabela `project_technologies`) |
| **Feedback**: comentário e uma nota (1 a 5) | pertence a um Project (N:1) |

```
app/
├── main.py              # monta o FastAPI: textos do Swagger, ordem das rotas e o / que leva ao /docs
├── core/
│   ├── database.py      # lê a DATABASE_URL, abre uma conexão por requisição e cria as tabelas
│   ├── errors.py        # BusinessError e as filhas, e o manipulador que padroniza os erros
│   └── types.py         # textos já validados: obrigatório, opcional e o filtro da URL
└── modules/             # um pacote por entidade, todos com as mesmas quatro camadas
    ├── profiles/
    ├── technologies/
    ├── projects/        # também a busca por tecnologia, as páginas e as estrelas
    └── feedbacks/       # também o cálculo da média
postman/
└── DevShowcase-Grupo4.postman_collection.json   # o roteiro de testes do vídeo
```

Dentro de cada módulo o caminho de uma requisição é sempre o mesmo:

- **router.py** recebe a chamada HTTP e diz quais DTOs entram e saem;
- **schemas.py** tem os DTOs: o que entra (com as validações) e o que sai;
- **service.py** aplica as regras: e-mail sem repetir, tecnologia sem repetir, perfil e tecnologias que precisam existir, cálculo da média;
- **repository.py** conversa com o banco em SQL.

## Coleção do Postman: em que ordem rodar?

| Pasta | O que mostra |
|---|---|
| **0 - Montar a vitrine** | cria 5 tecnologias, 2 perfis (Elismar e Kaenny) e 6 projetos (academia, lanchonete, pet shop...) e anota os ids |
| **1 - Tecnologias**, **2 - Perfis**, **3 - Projetos** | o que já existia na etapa 1, com os erros de cada cadastro |
| **4 - Listagem: filtro e páginas** | páginas, filtro por FastAPI escrito de três jeitos, página depois do fim, erros `400` e rota que não existe |
| **5 - Estrelas (upvote)** | 1ª e 2ª estrela num projeto novo, projeto que não existe e id `xyz` |
| **6 - Feedbacks e média** | nota 5 (média 5.0), nota 3 (média 4.0), média gravada no projeto, nota 10, nota `"cinco"`, JSON com aspas simples e projeto que não existe |

Toda requisição tem teste do status esperado, e os erros ficam no fim da pasta do assunto.

**E se precisar regravar um pedaço do vídeo?** Dá para clicar *Send* de novo em qualquer requisição, ou rodar uma pasta sozinha, sem teste vermelho:

- a pasta **0** aceita `201` ou `409` nas tecnologias e usa `{{$timestamp}}` nos e-mails;
- a pasta **4** confere cada resposta por ela mesma (ordem, filtro, totais), então a ordem em que as requisições rodam não importa;
- as pastas **5** e **6** não aproveitam projetos antigos: o *Pre-request* da primeira requisição cria um projeto só para a demonstração (Pet Shop Agenda e Quiz de Teoria Musical), e os testes esperam números exatos (1 e depois 2 estrelas; média 5.0 e depois 4.0). As requisições seguintes conferem se o projeto está no ponto certo antes de enviar; se não estiver (porque o *Send* foi clicado de novo, ou as variáveis estão vazias), preparam outro projeto já com as estrelas ou notas que faltam.
