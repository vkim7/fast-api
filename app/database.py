from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create a database URL for SQLAlchemy
# Format: postgresql://<username>:<password>@<ip-address>/<hostname>/<database_name>
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DB_USERNAME}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Each instance of the SessionLocal class will be a database session. The class itself is not a database session yet.
# But once we create an instance of the SessionLocal class, this instance will be the actual database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# returns class used to create database models or classes(ORM models)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
