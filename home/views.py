
from datetime import date

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Movie

PAGE_SIZE = 24


def render_movies(request, movies, template, **context):
    page_obj = Paginator(movies, PAGE_SIZE).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return render(request, template, {
        **context,
        "movies": page_obj.object_list,
        "page_obj": page_obj,
        "pagination_query": query.urlencode(),
    })


def home(request):
    return render_movies(request, Movie.objects.order_by("-release_date", "-pk"), "home.html")


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})


def search(request):
    query = request.GET.get('q', '').strip()[:100]
    movies = Movie.objects.filter(title__icontains=query).order_by("-release_date", "-pk") if query else Movie.objects.none()
    return render_movies(request, movies, "search_result.html", query=query)


def genre(request, genre_name):
    movies = Movie.objects.filter(genre__icontains=genre_name).order_by("-release_date", "-pk")
    return render_movies(request, movies, "genre.html", genre=genre_name)


def director(request, director_name):
    movies = Movie.objects.filter(director__icontains=director_name).order_by("-release_date", "-pk")
    return render_movies(request, movies, "director.html", director=director_name)


def rating(request, rating_value):
    movies = Movie.objects.filter(rating__gte=rating_value).order_by("-rating", "-pk")
    return render_movies(request, movies, "rating.html", rating=rating_value)


def release_year(request, year):
    movies = Movie.objects.filter(release_date__year=year).order_by("-release_date", "-pk")
    return render_movies(request, movies, "release_year.html", year=year)


def top_rated(request):
    movies = Movie.objects.order_by("-rating", "-pk")[:10]
    return render_movies(request, movies, "top_rated.html")


def upcoming(request):
    movies = Movie.objects.filter(release_date__gt=date.today()).order_by("release_date", "pk")
    return render_movies(request, movies, "upcoming.html")


def popular(request):
    movies = Movie.objects.order_by("-rating", "-release_date", "-pk")[:20]
    return render_movies(request, movies, "popular.html")


def random(request):
    movies = Movie.objects.order_by("?")[:10]
    return render_movies(request, movies, "random.html")
