from dataclasses import dataclass, asdict

import psycopg2
from psycopg2 import OperationalError, ProgrammingError, connect
from app.db import crud
from app.settings import settings


@dataclass
class ConnectionData:
    database: str
    user: str
    password: str
    host: str = "127.0.0.1"
    port: int = 5432


connection_data = ConnectionData(
    database=settings.postgres_db,
    user=settings.postgres_user,
    password=settings.postgres_password
)


def create_connection(connection_data: ConnectionData):
    connection = None
    try:
        connection = connect(**asdict(connection_data))
        print('Connection to PostgreSQL DB successful')
    except (OperationalError, ProgrammingError) as e:
        print(f'''The error '{e}' while creating connection occurred''')
    return connection


def create_cursor(connection):
    cursor = None
    try:
        cursor = connection.cursor()
    except (OperationalError, ProgrammingError) as e:
        print(f'''The error '{e}' while creating cursor occurred''')
        raise
    return cursor


def execute_query(connection, query: str, query_data: list = None, autocommit=True,
                  success_message='Query executed successfully') -> None:
    try:
        connection.autocommit = autocommit
        cursor = create_cursor(connection)
        if query_data is not None:
            cursor.execute(query, query_data)
        else:
            cursor.execute(query)
        print(success_message)
    except (OperationalError, ProgrammingError, psycopg2.errors.CheckViolation) as e:
        print(f'''The error '{e}' occurred''')
    if not autocommit:
        connection.commit()


def execute_read_query(connection, query, query_data: list = None) -> list[tuple] | None:
    try:
        cursor = create_cursor(connection)
        if query_data is not None:
            cursor.execute(query, query_data)
        else:
            cursor.execute(query)
        print("q")
        result = cursor.fetchall()
        return result
    except (OperationalError, ProgrammingError, psycopg2.errors.CheckViolation) as e:
        print(f'''The error '{e}' occurred''')


def create_tables(connection) -> None:
    create_users_table = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            is_admin BOOLEAN NOT NULL,
            hashed_password VARCHAR(255) NOT NULL
        );
    '''
    execute_query(connection, create_users_table, success_message="Table users was created successfully")

    create_todos_table = '''
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                owner_id INTEGER REFERENCES users(id) NOT NULL
            );
        '''
    execute_query(connection, create_todos_table, success_message="Table todos was created successfully")
