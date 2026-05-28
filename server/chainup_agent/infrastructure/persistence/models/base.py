from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy metadata anchor for Alembic and create_all."""

    pass
