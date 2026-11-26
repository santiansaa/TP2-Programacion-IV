
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event

DATABASE_URL = "sqlite:///biblioteca.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def activar_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def crear_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session
