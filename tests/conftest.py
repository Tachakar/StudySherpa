from collections.abc import Callable, Iterable
from io import BytesIO

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from studysherpa.api.main import app
from studysherpa.core.config import settings
from studysherpa.core.database import get_db

test_engine = create_async_engine(settings.test_database_url)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.connect() as connection:
        await connection.begin()

        async with TestSessionLocal(
            bind=connection, join_transaction_mode="create_savepoint"
        ) as session:
            yield session

        await connection.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", settings.test_database_url)
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from studysherpa.api.main import limiter

    limiter.reset()
    yield


@pytest.fixture()
def pdf_factory() -> Iterable[Callable[[int, bool], bytes]]:
    def _make_pdf(num_pages: int, include_images: bool) -> bytes:
        stream = BytesIO()
        pdf = canvas.Canvas(stream, pagesize=A4)
        for i in range(num_pages):
            text = pdf.beginText(20, 800)
            for _ in range(25):
                text.textLine("test " * 50)
            pdf.drawText(text)
            if include_images and i % 2 == 1:
                pdf.drawImage(
                    image=ImageReader(Image.new("RGB", size=(50, 50))), x=20, y=20
                )
            pdf.showPage()
        pdf.save()
        return stream.getvalue()

    yield _make_pdf
