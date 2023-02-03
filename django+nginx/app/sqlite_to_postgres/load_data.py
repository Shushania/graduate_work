import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from postgres_saver import PostgresSaver
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from sql_dataclass import (Filmwork, Genre, GenreFilmwork, Person,
                           PersonFilmwork)
from sqlite_loader import SQLiteLoader

load_dotenv()


@contextmanager
def conn_context_sqlite(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@contextmanager
def conn_context_postgres(dsl: dict):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    yield conn
    conn.close()


def saver_to_postgres(func, dataclass, sqlite_curs: sqlite3.Cursor):
    batch_size = 100
    while True:
        result = sqlite_curs.fetchmany(batch_size)
        if result:
            data = [dict(item) for item in result]
            [item.pop('file_path', None) for item in data]
            func([dataclass(**item) for item in data])
        else:
            break


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    sqlite_loader = SQLiteLoader(sqlite_conn)
    postgres_saver = PostgresSaver(pg_conn)
    # Сохранение в content.film_work
    saver_to_postgres(
        postgres_saver.save_filmwork,
        Filmwork,
        sqlite_loader.load_film_work())
    # Сохранение в content.person
    saver_to_postgres(
        postgres_saver.save_person,
        Person,
        sqlite_loader.load_person()
    )
    # Сохранение в content.genre
    saver_to_postgres(
        postgres_saver.save_genre,
        Genre,
        sqlite_loader.load_genre()
    )
    # Сохранение в content.genre_film_work
    saver_to_postgres(
        postgres_saver.save_genre_film_work,
        GenreFilmwork,
        sqlite_loader.load_genre_film_work()
    )
    # Сохранение в content.person_film_work
    saver_to_postgres(
        postgres_saver.save_person_film_work,
        PersonFilmwork,
        sqlite_loader.load_person_film_work()
    )


if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent
    dsl = {
        'dbname': os.environ.get('POSTGRES_NAME'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('POSTGRES_HOST'),
        'port': os.environ.get('POSTGRES_PORT')
    }
    print(os.path.join(BASE_DIR, os.environ.get('SQLITE_FILE')))
    with conn_context_sqlite(
            os.path.join(BASE_DIR, os.environ.get('SQLITE_FILE'))
    ) as sqlite_conn, \
         conn_context_postgres(dsl) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
