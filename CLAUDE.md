# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `Tachakar/StudySherpa`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`); `ready-for-agent` is never applied in this repo. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root, created lazily. See `docs/agents/domain.md`.
