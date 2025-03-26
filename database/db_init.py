from peewee import PostgresqlDatabase

import config

def connect_to_database() -> PostgresqlDatabase:
    return PostgresqlDatabase(
        config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST, port=config.DB_PORT,
    )
