from database.db_init import connect_to_database
from database.models import *


def init_db() -> None:
    """Database models to tables"""
    if not active_models:
        return
    with connect_to_database() as psql_db:
        psql_db.create_tables(active_models)

# Example of session connection:
# with connect_to_database() as db:
#     pass
