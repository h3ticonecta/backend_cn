# PlayHub — Backend (Django)

API REST e painel **Django Admin** para a landing [PlayHub — Jogos Online](../frontend_cn).

## Setup rápido (Windows)

```powershell
cd C:\Users\Gustavo\Documents\GitHub\backend_cn
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_playhub
python manage.py createsuperuser
python manage.py runserver
```

### Super Admin (Django)

1. Acesse **http://127.0.0.1:8000/admin/**
2. Entre com o usuário criado em `createsuperuser` (ou use as variáveis em `.env` com `createsuperuser --noinput`).

Criação não interativa:

```powershell
$env:DJANGO_SUPERUSER_USERNAME="admin"
$env:DJANGO_SUPERUSER_EMAIL="admin@playhub.local"
$env:DJANGO_SUPERUSER_PASSWORD="PlayHub@Admin2026"
python manage.py createsuperuser --noinput
```

No admin você gerencia: **Jogos**, **Provedores**, **Ao vivo**, **Promoções** e **Banner hero**.

## API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/home/` | Payload completo (games, categories, live, promos, hero) |
| GET | `/api/v1/games/?category=slots&search=aviator` | Lista de jogos filtrada |
| GET | `/api/v1/games/roleta-brasil/` | Card Roleta + meta `play` + config da mesa |
| GET | `/api/v1/categories/` | Abas de categoria |
| GET | `/api/v1/providers/` | Provedores |
| GET | `/api/v1/live/` | Mesas ao vivo |
| GET | `/api/v1/promotions/` | Promoções |
| GET | `/api/v1/hero/` | Banner principal |
| GET/POST | `/api/v1/roleta/…` | Jogo Roleta (demo) — [contrato](./docs/contratos/roleta.md) |

O JSON de cada jogo segue o tipo `Game` do frontend (`id`, `title`, `provider`, `category`, `badge`, `rtp`, `gradient`, `icon`).

CORS liberado para `http://localhost:5173` por padrão (Vite).

## Deploy (Railway / Gunicorn)

O start usa **Gunicorn** (`requirements.txt`). Se o log mostrar `gunicorn: command not found`, faça redeploy após atualizar o repositório.

Variáveis recomendadas em produção:

| Variável | Exemplo |
|----------|---------|
| `DJANGO_SECRET_KEY` | string longa aleatória |
| `DJANGO_DEBUG` | `false` |
| `DATABASE_URL` | Postgres (addon Railway) |
| `DJANGO_ALLOWED_HOSTS` | `backendcn-dev.up.railway.app` (domínio público da API) |
| `CORS_ALLOWED_ORIGINS` | `https://frontendcn-dev.up.railway.app` (URL do frontend) |

Se `GET /api/v1/home/` retorna **400** com *DisallowedHost*, o host não está em `ALLOWED_HOSTS`. Defina `DJANGO_ALLOWED_HOSTS` ou atualize o `settings.py` (wildcard `.up.railway.app` em deploy Railway).

No Railway, o start já roda `seed_playhub` e `seed_roleta` (ver `Procfile` / `nixpacks.toml`). Se a home vier com `games: []`, execute no shell do serviço:

```bash
python manage.py seed_playhub
python manage.py seed_roleta
```

Após o primeiro deploy com banco persistente:

```bash
python manage.py createsuperuser
```

Ou defina `DJANGO_SUPERUSER_*` e rode `createsuperuser --noinput` no shell do Railway.

## Banco de dados

SQLite em `db.sqlite3` (desenvolvimento). Em produção, use `DATABASE_URL` (PostgreSQL).

Repopular dados do frontend:

```powershell
python manage.py seed_playhub --reset
```
