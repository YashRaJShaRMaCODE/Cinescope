from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, TestCase
from datetime import date, timedelta

from django.urls import reverse

from .models import Movie


class ProductionCookieSettingsTests(SimpleTestCase):
    def test_auth_cookies_are_https_only_when_debug_is_off(self):
        self.assertEqual(settings.SESSION_COOKIE_SECURE, not settings.DEBUG)
        self.assertEqual(settings.CSRF_COOKIE_SECURE, not settings.DEBUG)
        if not settings.DEBUG:
            self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))
            self.assertEqual(settings.SECURE_HSTS_SECONDS, 31_536_000)
            request = RequestFactory().get("/", HTTP_X_FORWARDED_PROTO="https")
            self.assertTrue(request.is_secure())


class MoviePaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Movie.objects.bulk_create([
            Movie(
                title=f"Sky Story {number}",
                description="A story among the stars.",
                release_date=date(2020, 1, 1) + timedelta(days=number),
                genre="Sci-Fi",
                director="A. Director",
                rating=7.0 + number / 100,
                poster_url=f"https://example.com/posters/{number}.jpg",
            )
            for number in range(25)
        ])

    def test_home_lists_24_movies_and_links_to_the_next_page(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 24)
        self.assertEqual(response.context["page_obj"].paginator.count, 25)
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, "page=2")

    def test_search_pagination_keeps_the_search_term(self):
        response = self.client.get(reverse("search"), {"q": "Sky", "page": "2"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["movies"]), 1)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(response.context["pagination_query"], "q=Sky")
        self.assertContains(response, "q=Sky&amp;page=1")

    def test_invalid_page_uses_first_and_out_of_range_page_uses_last(self):
        invalid = self.client.get(reverse("home"), {"page": "not-a-number"})
        too_large = self.client.get(reverse("home"), {"page": "999"})

        self.assertEqual(invalid.context["page_obj"].number, 1)
        self.assertEqual(too_large.context["page_obj"].number, 2)
