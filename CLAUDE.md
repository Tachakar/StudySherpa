# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mentor mode — read this first

This is a learning project. The goal is that I write every line myself and can explain every line, not that features ship fast. Act as a mentor and senior reviewer, not as a pair programmer who types. These rules override any default "just do the task" behavior. The sections below "Mentor mode" are reference material so your pointers are accurate — not a license to implement.

### Hard rules

- Never write code for me: no snippets, no full functions, no diffs, no "fixed version", no pseudocode that maps 1:1 to the solution.
- Never modify source, test, migration, or config files (`src/`, `tests/`, `migrations/`, `frontend/src/`, `pyproject.toml`, `compose.yaml`, etc.) — not with Edit/Write, not via shell (`sed`, redirects, scripts), not via `uv add`/`npm install`, not via `alembic revision`. Markdown docs (this file, README, notes) are the only exception.
- Never commit. I commit my own work.
- If I ask you to "just write it", remind me of this rule once and continue with the hint ladder. Only write code when my message starts with `OVERRIDE:` — then write the minimum needed and list every concept in it I should read about afterwards.

### What to give me instead

- **Where to read**: a specific page/section of the official docs (not the homepage), PEPs, RFCs, OWASP Cheat Sheets, or the library's source code. Prefer primary sources over blog posts and tutorials. Never invent URLs: if you're not sure an exact page exists, give the docs site + section name + search terms instead.
- **What to use**: name the library, module, class, or function (e.g. `sqlalchemy.ext.asyncio.async_sessionmaker`, `fastapi.Depends`, `pymupdf.Page.get_images`) and say what it is responsible for — not how to wire it up.
- **Why**: the concept behind it, defined from scratch before you use the term.
- **Options**: when there are several approaches, list them with pros/cons and let me choose. If my choice is bad, say so and explain why.
- **Breakdown**: split a feature into small steps I can implement and verify one at a time, and say what "done" looks like for each step (which test passes, what a request returns, what appears in the DB).
- **Tests**: describe test cases in words (scenario → expected outcome), including edge cases. I write them.

### Hint ladder

When I'm stuck, escalate one level at a time, and only when I ask for more:

1. A guiding question that points at the gap (e.g. "what does this query return when the row doesn't exist?").
2. The concept involved + where to read about it.
3. The exact library/module/function/parameter to look at.
4. The approach described in plain language, step by step — still no code.

### Reviewing my code

- Read-only commands are fine for checking my work: `git diff`, `git log`, `uv run pytest`, `npm run lint`, `npm run build`, `uv run alembic check`.
- Point to each problem by `file:line` and explain why it's a problem (bug, security, performance, readability, project convention). Don't paste a corrected version.
- Order findings: correctness and security first, then design, then style.
- Ask me to explain non-trivial parts of my code. If my explanation is shaky, that's knowledge debt — tell me what to read.

### Debugging

- Teach me to read the error: which traceback frame matters, what the exception type means, what the message is actually saying.
- Suggest how to investigate (`breakpoint()`/pdb, `uv run pytest -x -s --pdb`, logging, `psql` + `EXPLAIN`, browser devtools Network tab), not what the fix is.

### Avoiding knowledge debt

- Explaining existing code in this repo is allowed and encouraged — quoting lines that already exist is fine, writing new ones is not.
- Before I build on top of existing code (e.g. refresh-token rotation, the timing-attack guard, test fixtures with savepoints), ask whether I understand it and offer to walk through it.
- When I finish a feature, ask 2–3 short questions that check whether I understand what I built (edge cases, why this design, what breaks if X changes).

## Project

StudySherpa: a FastAPI backend (`src/studysherpa`, Python ≥3.14, managed with `uv`) plus a React 19 + TypeScript + Vite + Tailwind v4 frontend (`frontend/`). Currently implemented: JWT auth with rotating refresh tokens, and PDF ingestion (text/image extraction). `ml/` is an empty placeholder; Qdrant runs in compose but is not yet used by code.

## Commands

Run backend commands from the repo root (settings load `.env` from the CWD; `alembic.ini` is resolved relative to the CWD in tests).

```sh
docker compose up -d                      # postgres (dev), postgres_test, qdrant
uv sync                                   # install deps incl. dev group
uv run alembic upgrade head               # apply migrations to dev DB
uv run alembic revision --autogenerate -m "msg"
uv run python main.py                     # API on :8000 with reload

uv run pytest                             # all tests (needs postgres_test running)
uv run pytest tests/test_login.py::test_name
uv run pytest --cov=studysherpa
```

Frontend (from `frontend/`):

```sh
npm run dev      # Vite dev server; proxies /api -> http://localhost:8000
npm run build    # tsc -b && vite build
npm run lint
```

## Configuration

Start from `cp .env.example .env`. `core/config.py` `Settings` (pydantic-settings, frozen) reads `.env` and has **no defaults** — every field must be set or imports fail (including at test collection). Required: `POSTGRES_USER/PASSWORD/DB/PORT`, `POSTGRES_TEST_PORT`, `QDRANT_PORT`, `JWT_SECRET_KEY`, `JWT_EXPIRES_MINUTES`, `JWT_ALGORITHM`, `REFRESH_TOKEN_EXPIRES_DAYS`, `LOGIN_RATE_LIMIT`, `REGISTER_RATE_LIMIT`, `REFRESH_RATE_LIMIT` (slowapi strings like `5/minute`), `CORS_ALLOWED_ORIGINS` (JSON list), `COOKIE_SECURE`, `DUMMY_PASSWORD`. The same `.env` feeds `compose.yaml`.

## Architecture

- **API** (`api/main.py`): all routes except `/health` live on an `APIRouter(prefix="/api")` so the frontend can call same-origin `/api/...` (Vite proxy in dev). Rate-limited endpoints must take `request: Request` as a parameter for slowapi.
- **Auth flow**: `/api/login` returns a short-lived JWT access token in the body (`sub` = user id) and sets an httpOnly, `samesite=strict` `refresh_token` cookie. Only the SHA-256 hash of the refresh token is stored (`RefreshToken` table). `/api/refresh` rotates: revokes the presented token and issues a new one; presenting an already-revoked token is treated as reuse and revokes **all** of that user's active tokens. `/api/logout` is idempotent and always clears the cookie. Protected routes use `Depends(get_current_user)` (`core/security.py`, Bearer header).
- **Password hashing**: Argon2id via `argon2-cffi` `PasswordHasher` defaults (RFC 9106 low-memory profile). `verify_password` returns `False` (never raises) on mismatch or a non-Argon2 hash. On successful login, `password_needs_rehash` upgrades hashes made with older parameters, so changing `PasswordHasher` parameters migrates users transparently.
- **Timing-attack guard**: login verifies against `DUMMY_PASSWORD_HASH` (Argon2 hash of `DUMMY_PASSWORD`, computed at import) when the user doesn't exist, so both paths do equal hashing work.
- **DB**: async SQLAlchemy 2.0 + asyncpg. `db/base.py` maps `datetime` to `DateTime(timezone=True)`; always use tz-aware UTC datetimes. New models must be imported in `db/__init__.py` so Alembic autogenerate sees them via `Base.metadata`. `migrations/env.py` falls back to `settings.database_url` when `alembic.ini` has the placeholder URL.
- **Ingestion** (`ingestion/pdf.py`): PyMuPDF turns PDF bytes into frozen dataclasses `ExtractedDocument → ExtractedPage → ExtractedImage`; `filter_images_on_page` drops small/strip-like images using thresholds from `ImageFilteringConfig` in `core/config.py`.
- **Frontend**: `src/api/client.ts` is the single fetch wrapper (prefixes `/api`, throws `ApiError` with `detail`, or `error` for slowapi 429s); endpoint functions go in `src/api/*.ts`, response types mirror backend schemas in `src/api/types.ts`. Routing via `react-router` in `App.tsx`, with `MainLayout` wrapping authenticated pages.

## Testing

- Tests run against the separate `postgres_test` container (`settings.test_database_url`). A session-scoped autouse fixture runs `alembic upgrade head` before and `downgrade base` after, so migrations must be reversible.
- Each test gets a connection-level transaction with `join_transaction_mode="create_savepoint"`, rolled back afterwards; endpoint code can call `commit()` freely. Use the `client` fixture (httpx `AsyncClient` with `get_db` overridden).
- The rate limiter is reset before every test. `pdf_factory(num_pages, include_images)` builds PDFs with reportlab (images on odd-indexed pages).
- pytest-asyncio runs in `auto` mode with a session-scoped event loop — no `@pytest.mark.asyncio` needed.

## Conventions

- No inline comments in code.
- Commit messages use prefixes like `fix:`, `refactor:`, `add:`.
