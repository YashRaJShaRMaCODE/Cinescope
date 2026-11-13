
from datetime import date
import json

from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
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


def healthz(_request):
    return JsonResponse({"status": "ok"})


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    return HttpResponse(
        f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {sitemap_url}\n",
        content_type="text/plain",
    )


def home(request):
    movies = Movie.objects.all()
    genre_counts = list(Movie.objects.values("genre").annotate(count=Count("id")).order_by("genre"))
    genres = [item["genre"] for item in genre_counts]
    years = [value.year for value in Movie.objects.dates("release_date", "year", order="DESC")]
    genre = request.GET.get("genre", "")
    year = request.GET.get("year", "")
    rating = request.GET.get("rating", "")
    sort = request.GET.get("sort", "latest")

    if genre in genres:
        movies = movies.filter(genre=genre)
    else:
        genre = ""
    if year.isdigit() and int(year) in years:
        year = int(year)
        movies = movies.filter(release_date__year=year)
    else:
        year = ""
    if rating in {"6", "7", "8", "9"}:
        rating = int(rating)
        movies = movies.filter(rating__gte=rating)
    else:
        rating = ""

    ordering = {
        "latest": ("-release_date", "-pk"),
        "rating": ("-rating", "-release_date"),
        "title": ("title", "pk"),
    }
    if sort not in ordering:
        sort = "latest"
    return render_movies(
        request,
        movies.order_by(*ordering[sort]),
        "home.html",
        genres=genres,
        genre_counts=genre_counts,
        years=years,
        selected_genre=genre,
        selected_year=year,
        selected_rating=rating,
        selected_sort=sort,
        rating_steps=(6, 7, 8, 9),
        empty_message="No films match those filters. Try widening your selection.",
    )


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return_to = request.GET.get("return_to", "")
    if not url_has_allowed_host_and_scheme(
        return_to, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return_to = reverse("home")
    related_query = Q()
    if movie.genre.strip():
        related_query |= Q(genre__iexact=movie.genre)
    if movie.director.strip():
        related_query |= Q(director__iexact=movie.director)
    related_movies = (
        Movie.objects.filter(related_query).exclude(pk=movie.pk).order_by("-rating", "title", "pk")[:4]
        if related_query else Movie.objects.none()
    )
    movie_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Movie",
        "name": movie.title,
        "image": movie.poster_url,
        "datePublished": movie.release_date.isoformat(),
        "director": {"@type": "Person", "name": movie.director},
        "description": movie.description,
    }, ensure_ascii=False).replace("<", "\\u003C").replace(">", "\\u003E").replace("&", "\\u0026")
    return render(request, "movie_detail.html", {
        "movie": movie,
        "related_movies": related_movies,
        "detail_return_url": return_to,
        "share_url": request.build_absolute_uri(reverse("movie_detail", args=[movie.pk])),
        "movie_schema": mark_safe(movie_schema),
    })


def search(request):
    query = request.GET.get('q', '').strip()[:100]
    search_query = (
        Q(title__icontains=query) | Q(genre__icontains=query) | Q(director__icontains=query)
        | Q(description__icontains=query)
    )
    if query.isdigit():
        search_query |= Q(release_date__year=int(query))
    if query:
        rank_rules = [
            When(title__iexact=query, then=Value(0)),
            When(title__istartswith=query, then=Value(1)),
            When(title__icontains=query, then=Value(2)),
            When(Q(genre__icontains=query) | Q(director__icontains=query), then=Value(3)),
        ]
        if query.isdigit():
            rank_rules.append(When(release_date__year=int(query), then=Value(4)))
        ordering = Case(
            *rank_rules,
            default=Value(5),
            output_field=IntegerField(),
        )
        movies = Movie.objects.filter(search_query).annotate(search_rank=ordering).order_by(
            "search_rank", "-release_date", "-pk"
        )
    else:
        movies = Movie.objects.none()
    return render_movies(
        request,
        movies,
        "search_result.html",
        query=query,
        empty_message=(
            "Enter a title, genre, director, release year or plot detail in the search above."
            if not query else "No matching films. Try a different title, genre, director, year or plot detail."
        ),
    )


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
