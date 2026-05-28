from sqlmodel import SQLModel, Session, create_engine
from core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.effective_database_url,
    echo=settings.db_echo,
)


def create_db_and_tables() -> None:
    """Create all tables on startup."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a DB session per request."""
    with Session(engine) as session:
        yield session