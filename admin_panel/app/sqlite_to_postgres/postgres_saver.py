from dataclasses import asdict

from psycopg2.extras import execute_values
from sql_dataclass import (Filmwork, Genre, GenreFilmwork, Person,
                           PersonFilmwork)


class PostgresSaver(object):

    def __init__(self, conn):
        self.curs = conn.cursor()
        self.conn = conn

    def save_filmwork(self, filmworks: [Filmwork]):

        values = [list(asdict(filmwork).values()) for filmwork in filmworks]
        sql = 'INSERT INTO content.film_work (title, description, type, ' \
              'creation_date, created_at, updated_at, rating, id) ' \
              'VALUES %s ON CONFLICT (id) DO NOTHING;'
        execute_values(self.curs, sql, values)
        self.conn.commit()

    def save_person(self, persons: [Person]):

        values = [list(asdict(person).values()) for person in persons]
        sql = 'INSERT INTO content.person (full_name, created_at, ' \
              'updated_at, id) VALUES %s ON CONFLICT (id) DO NOTHING;'
        execute_values(self.curs, sql, values)
        self.conn.commit()

    def save_genre(self, genres: [Genre]):

        values = [list(asdict(genre).values()) for genre in genres]
        sql = 'INSERT INTO content.genre (name, description, created_at, ' \
              'updated_at, id) VALUES %s ON CONFLICT (id) DO NOTHING;'
        execute_values(self.curs, sql, values)
        self.conn.commit()

    def save_genre_film_work(self, genre_film_works: [GenreFilmwork]):

        values = [list(asdict(genre_film_work).values())
                  for genre_film_work in genre_film_works]
        sql = 'INSERT INTO content.genre_film_work (film_work_id, genre_id, ' \
              'created_at, id) VALUES %s ON CONFLICT (film_work_id, ' \
              'genre_id) DO NOTHING;'
        execute_values(self.curs, sql, values)
        self.conn.commit()

    def save_person_film_work(self, person_film_works: [PersonFilmwork]):

        values = [list(asdict(person_film_work).values())
                  for person_film_work in person_film_works]
        sql = 'INSERT INTO content.person_film_work (film_work_id, ' \
              'person_id, role, created_at, id) VALUES %s ON CONFLICT ' \
              '(film_work_id, person_id, role) DO NOTHING;'
        execute_values(self.curs, sql, values)
        self.conn.commit()
