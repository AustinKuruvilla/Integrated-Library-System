import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'p455word'),
    'database': os.environ.get('DB_NAME', 'library_management'),
}


def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as exc:
        host = DB_CONFIG.get('host')
        port = DB_CONFIG.get('port', 3306)
        if getattr(exc, 'errno', None) == 2003:
            raise RuntimeError(
                f"Cannot connect to MySQL server at {host}:{port}. "
                "Make sure MySQL is running and the connection settings in db.py are correct."
            ) from exc
        raise RuntimeError(f"Database connection error: {exc}") from exc
