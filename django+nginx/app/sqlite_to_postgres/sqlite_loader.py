
class SQLiteLoader(object):

    def __init__(self, conn):
        self.curs = conn.cursor()

    def load_genre(self):
        self.curs.execute("SELECT * FROM genre;")
        return self.curs

    def load_person(self):
        self.curs.execute("SELECT * FROM person;")
        return self.curs

    def load_film_work(self):
        self.curs.execute("SELECT * FROM film_work;")
        return self.curs

    def load_genre_film_work(self):
        self.curs.execute("SELECT * FROM genre_film_work;")
        return self.curs

    def load_person_film_work(self):
        self.curs.execute("SELECT * FROM person_film_work;")
        return self.curs
