
from datetime import date

from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
def home(request):
    movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies}) 
from django.shortcuts import get_object_or_404

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})
def search(request):
    query = request.GET.get('q')
    movies = Movie.objects.filter(title__icontains=query)
    return render(request, 'search_results.html', {'movies': movies, 'query': query})
def genre(request, genre_name):
    movies = Movie.objects.filter(genre__icontains=genre_name)
    return render(request, 'genre.html', {'movies': movies, 'genre': genre_name})
def director(request, director_name):
    movies = Movie.objects.filter(director__icontains=director_name)
    return render(request, 'director.html', {'movies': movies, 'director': director_name})
def rating(request, rating_value):
    movies = Movie.objects.filter(rating__gte=rating_value)
    return render(request, 'rating.html', {'movies': movies, 'rating': rating_value})
def release_year(request, year):
    movies = Movie.objects.filter(release_date__year=year)
    return render(request, 'release_year.html', {'movies': movies, 'year': year})
def top_rated(request):
    movies = Movie.objects.order_by('-rating')[:10]
    return render(request, 'top_rated.html', {'movies': movies})


def upcoming(request):
    movies = Movie.objects.filter(release_date__gt=date.today()).order_by('release_date')
    return render(request, 'upcoming.html', {'movies': movies})
def popular(request):
    movies = Movie.objects.order_by('-rating')[:20]
    return render(request, 'popular.html', {'movies': movies})
def random(request):
    movies = Movie.objects.order_by('?')[:10]
    return render(request, 'random.html', {'movies': movies})
def movie_grid(request):
    movies = Movie.objects.all()
    return render(request, 'movie_grid.html', {'movies': movies})   
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})

# Create your views here.
