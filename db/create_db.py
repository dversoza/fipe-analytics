from sqlalchemy import Engine

from db.engine import create_db_engine
from db.models.base import mapper_registry


def create_db(_engine: Engine):
    """Create the database tables."""

    # We must import all models to create the tables
    from db.models import all_models  # noqa

    mapper_registry.metadata.create_all(_engine)


if __name__ == "__main__":
    _engine = create_db_engine()

    create_db(_engine)
