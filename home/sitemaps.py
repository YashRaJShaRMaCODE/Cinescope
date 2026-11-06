from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Movie


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ["home", "popular", "top_rated", "upcoming"]

    def location(self, item):
        return reverse(item)


class MovieSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Movie.objects.order_by("pk")

    def location(self, item):
        return reverse("movie_detail", args=[item.pk])


class GenreSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Movie.objects.order_by("genre").values_list("genre", flat=True).distinct()

    def location(self, item):
        return reverse("genre", args=[item])


class DirectorSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Movie.objects.order_by("director").values_list("director", flat=True).distinct()

    def location(self, item):
        return reverse("director", args=[item])


class ReleaseYearSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Movie.objects.dates("release_date", "year", order="DESC")

    def location(self, item):
        return reverse("release_year", args=[item.year])
