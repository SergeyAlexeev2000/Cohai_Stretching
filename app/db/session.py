# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# здесь можешь поставить свой PostgreSQL / SQLite / что угодно
# пока оставим простой пример на SQLite (чтобы оно точно завелось)
DATABASE_URL = "sqlite:///./cohai_stretching.db"
# если хочешь Postgres, будет так:
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost/cohai_stretching"

# создаём движок
engine = create_engine(
    DATABASE_URL,
    echo=False,      # можно True, если хочешь видеть SQL в консоли
    future=True,
)

# фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
