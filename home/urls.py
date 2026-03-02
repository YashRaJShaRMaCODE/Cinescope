from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search, name='search'),
    path('genre/<str:genre_name>/', views.genre, name='genre'),
    path('director/<str:director_name>/', views.director, name='director'),
    path('rating/<int:rating_value>/', views.rating, name='rating'),
    path('release-year/<int:year>/', views.release_year, name='release_year'),
    path('top-rated/', views.top_rated, name='top_rated'),
    path('upcoming/', views.upcoming, name='upcoming'),
    path('popular/', views.popular, name='popular'),
    path('random/', views.random, name='random'),
]