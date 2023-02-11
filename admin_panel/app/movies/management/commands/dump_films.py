import requests
from django.core.management.base import BaseCommand
from movies.models import (Filmwork, Genre, GenreFilmwork, Person,
                           PersonFilmwork)


class Command(BaseCommand):
    max_page=100

    def handle(self, *args, **kwargs):
        page = 1
        while page <= self.max_page:
            response_films = requests.get(f"https://kinobd.ru/api/films?page={page}")
            if response_films.status_code == 200:
                data = response_films.json().get("data", [])
                for film in data:
                    genres = []
                    persons_and_roles = []
                    try:
                        rating = round(float(film.get("rating_kp")), 1)
                    except:
                        continue
                    for genre in film.get("genres", []):
                        current_genres = Genre.objects.filter(name=genre.get("name_ru"))
                        if len(current_genres) < 1:
                            current_genre = Genre.objects.create(name=genre.get("name_ru"))
                        else:
                            current_genre = current_genres.first()
                        genres.append(current_genre)
                    for person in film.get("persons", []):
                        current_persons = Person.objects.filter(full_name=person.get("name_russian"))
                        if len(current_persons) < 1:
                            current_person = Person.objects.create(full_name=person.get("name_russian"))
                        else:
                            current_person = current_persons.first()
                        if person.get("profession", {}).get("profession_id") in ["director", "writer"]:
                            role = person.get("profession", {}).get("profession_id")
                        else:
                            role = "actor"
                        persons_and_roles.append(
                            {
                                "person": current_person,
                                "role": role
                            }
                        )
                    filmwork = Filmwork.objects.create(
                        title=film.get("name_russian"),
                        description=film.get("description"),
                        creation_date=film.get("premiere_ru"),
                        rating=rating
                    )
                    for genre in genres:
                        try:
                            GenreFilmwork.objects.create(
                                film_work=filmwork,
                                genre=genre
                            )
                        except:
                            pass
                    for person_and_role in persons_and_roles:
                        try:
                            PersonFilmwork.objects.create(
                                film_work=filmwork,
                                person=person_and_role.get("person"),
                                role=person_and_role.get("role")
                            )
                        except:
                            pass
                if page%5 == 0:
                    print(f"{50 * page} movies uploaded...")
                page += 1
            else:
                print(f"{response_films.status_code}")
                break