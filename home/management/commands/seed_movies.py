from datetime import date

from django.core.management.base import BaseCommand

from home.models import Movie

MOVIES = [
    ("Inception", "A thief who steals secrets through dreams is given one last job: plant an idea.", date(2010, 7, 16), "Sci-Fi", "Christopher Nolan", 8.8, "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg"),
    ("The Dark Knight", "Batman faces the Joker, a criminal mastermind who wants to watch Gotham burn.", date(2008, 7, 18), "Action", "Christopher Nolan", 9.0, "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"),
    ("Interstellar", "Explorers travel through a wormhole to find humanity a new home.", date(2014, 11, 7), "Sci-Fi", "Christopher Nolan", 8.7, "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"),
    ("3 Idiots", "Two friends search for their long-lost college buddy who taught them to think differently.", date(2009, 12, 25), "Comedy", "Rajkumar Hirani", 8.4, "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z8Tew.jpg"),
    ("Parasite", "A poor family schemes its way into the life of a wealthy household.", date(2019, 5, 30), "Thriller", "Bong Joon-ho", 8.5, "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"),
    ("Dangal", "A former wrestler trains his daughters to become world-class wrestlers.", date(2016, 12, 23), "Drama", "Nitesh Tiwari", 8.3, "https://image.tmdb.org/t/p/w500/1CoKNi3XVyijPCvy0usDbSWEXAg.jpg"),
]


class Command(BaseCommand):
    help = "Add sample movies if the table is empty"

    def handle(self, *args, **options):
        if Movie.objects.exists():
            return
        Movie.objects.bulk_create(Movie(title=t, description=d, release_date=r, genre=g, director=dr, rating=ra, poster_url=p)
                                  for t, d, r, g, dr, ra, p in MOVIES)
        self.stdout.write(f"Added {len(MOVIES)} movies")
