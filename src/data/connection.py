import mysql.connector
from mysql.connector import Error

from src import config
from src.domain.errors import ServiceUnavailable


def get_connection():
    try:
        return mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
        )
    except Error:
        raise ServiceUnavailable("Could not connect to the database.")

