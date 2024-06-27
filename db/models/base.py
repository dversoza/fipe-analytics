"""Defining Table Metadata with the ORM

When using the ORM, the MetaData collection remains present, however it itself is
contained within an ORM-only object known as the registry.

The registry, when constructed, automatically includes a MetaData object that will
store a collection of Table.

>>> mapper_registry.metadata
MetaData()

Instead of declaring Table objects directly, we will now declare them indirectly
through directives applied to our mapped classes.
In the most common approach, each mapped class descends from a common base class known
as the declarative base.
We get a new declarative base from the registry using registry.generate_base():

The steps of creating the registry and “declarative base” classes can be combined into
one step using the historically familiar declarative_base() function:

>>> from sqlalchemy.orm import declarative_base
>>> Base = declarative_base()

Ref: https://docs.sqlalchemy.org/en/14/tutorial/metadata.html#tutorial-orm-table-metadata
"""

from sqlalchemy.orm import registry

mapper_registry = registry()

SQLAlchemyDeclarativeBase = mapper_registry.generate_base(
    name="SQLAlchemyDeclarativeBase"
)


__all__ = ["mapper_registry", "SQLAlchemyDeclarativeBase"]
