import os
from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")

DB_NAME = os.getenv("PGDATABASE")

DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")


print(DB_HOST)




DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}"
    f"/{DB_NAME}"
)

print(DATABASE_URL)

raise Exception("STOP")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no configurada")

engine = create_engine(DATABASE_URL, echo=True)


