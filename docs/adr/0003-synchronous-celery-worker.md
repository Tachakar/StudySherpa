# Celery worker runs synchronous code in an async codebase

The API uses async SQLAlchemy with asyncpg, but mainline Celery runs tasks synchronously, so the worker has its own synchronous engine and sessions. Most worker time is CPU-bound (rendering pages, LibreOffice conversion, local embeddings), where async gives no benefit; the API stays responsive because this work runs in separate worker processes. Async would only help while waiting on vision-model calls, which we handle with worker concurrency, or a dedicated threads-pool queue, if it becomes the bottleneck.

## Considered Options

- **Wrapping async code in `asyncio.run` per task**: a new event loop per task, and async connection pools misbehave across loops.
- **Third-party asyncio worker pools** (`celery-aio-pool`, `celery-pool-asyncio`, `aio-celery`): small, young projects on the most critical path.
- **arq**: natively async and reuses the existing sessions; passed over for Celery's maturity and wider recognition.

## Consequences

Task bodies stay thin: each opens a sync session and calls a plain function that takes the session as a parameter. Those functions are tested with a sync rollback fixture mirroring the async one, because a real worker uses its own connections and cannot see a test's uncommitted rows.
