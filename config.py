import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

DB_USER: Final[str] = "postgres"
DB_PORT: Final[int] = 5432
DB_NAME: Final[str] = os.environ["db_name"]
DB_PASSWORD: Final[str] = os.environ["db_password"]
DB_HOST: Final[str] = os.environ["db_host"]
