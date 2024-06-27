from sqlalchemy import Engine, create_engine

DATABASE_URI = "postgresql+psycopg://myuser:mypassword@localhost:5432/mydb"


def create_db_engine():
    """The start of any SQLAlchemy application is an object called the Engine.

    This object acts as a central source of connections to a particular database,
    providing both a factory as well as a holding space called a connection pool for
    these database connections.
    The engine is typically a global object created just once for a particular database
    server, and is configured using a URL string which will describe how it should
    connect to the database host or backend.
    """
    DEBUG = False

    return create_engine(DATABASE_URI, echo=DEBUG, future=True)


def execute_statement(db_engine: Engine, statement: str):
    """Creates a connection to the database and execute a statement using the given
    database engine.

    Args:
        - db_engine: The database engine to use.
        - statement: The SQL statement to execute.

    Returns:
        - The result of the statement execution.
    """
    with db_engine.connect() as conn:
        result = conn.execute(statement)

    return result


__all__ = ["create_db_engine", "execute_statement"]
