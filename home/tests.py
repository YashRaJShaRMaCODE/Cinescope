from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from datetime import date, timedelta
import re

from django.urls import reverse

from .models import Movie


class ProductionCookieSettingsTests(SimpleTestCase):
    def test_auth_cookies_are_https_only_when_debug_is_off(self):
        self.assertEqual(settings.SESSION_COOKIE_SECURE, not settings.DEBUG)
        self.assertEqual(settings.CSRF_COOKIE_SECURE, not settings.DEBUG)
        if not settings.DEBUG:
            self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))
            self.assertEqual(settings.SECURE_HSTS_SECONDS, 31_536_000)
            self.assertTrue(settings.SECURE_SSL_REDIRECT)
            request = RequestFactory().get("/", HTTP_X_FORWARDED_PROTO="https")
            self.assertTrue(request.is_secure())


@override_settings(SECURE_SSL_REDIRECT=False)
class PublicSecurityHeaderTests(TestCase):
    def test_public_html_has_a_nonce_csp_and_restrictive_permissions(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        policy = response["Content-Security-Policy"]
        self.assertIn("script-src 'self' 'nonce-", policy)
        self.assertIn("script-src-attr 'none'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertEqual(response["Permissions-Policy"], "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["Referrer-Policy"], "strict-origin-when-cross-origin")
        self.assertEqual(response["Cross-Origin-Opener-Policy"], "same-origin")

    def test_movie_json_ld_script_receives_the_matching_nonce(self):
        movie = Movie.objects.create(
            title="Nonce Test",
            description="A test film.",
            release_date=date(2020, 1, 1),
            genre="Drama",
            director="A. Director",
            rating=7.5,
            poster_url="https://image.tmdb.org/t/p/w500/test.jpg",
        )
        response = self.client.get(reverse("movie_detail", args=[movie.pk]))
        nonce = re.search(r"'nonce-([^']+)'", response["Content-Security-Policy"]).group(1)

        self.assertContains(response, f'<script nonce="{nonce}" type="application/ld+json">')

    def test_admin_is_not_given_the_public_content_policy(self):
        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Content-Security-Policy", response)


@override_settings(SECURE_SSL_REDIRECT=False)
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

    def test_home_filters_and_sorts_the_catalog(self):
        response = self.client.get(reverse("home"), {
            "genre": "Sci-Fi", "year": "2020", "rating": "7", "sort": "rating",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 25)
        self.assertEqual(response.context["movies"][0].title, "Sky Story 24")
        self.assertContains(response, '<option value="2020" selected>2020</option>')
        self.assertContains(response, 'name="genre"')
        self.assertContains(response, "Clear filters")

    def test_home_shows_genres_with_catalog_counts(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.context["genre_counts"], [{"genre": "Sci-Fi", "count": 25}])
        self.assertContains(response, 'id="genres-title"')
        self.assertContains(response, 'href="/genre/Sci-Fi/"')
        self.assertContains(response, "25 films")

    def test_watchlist_controls_render_on_collection_and_detail_pages(self):
        listing = self.client.get(reverse("home"))
        self.assertContains(listing, 'id="cine-watchlist-toggle"')
        self.assertContains(listing, 'id="cine-watchlist-pick"')
        self.assertContains(listing, 'id="cine-watchlist-pick-result"')
        self.assertContains(listing, 'data-title="Sky Story 24"')
        self.assertContains(listing, 'aria-pressed="false"')

        detail = self.client.get(reverse("movie_detail", args=[Movie.objects.first().pk]))
        self.assertContains(detail, 'id="cine-watchlist"')
        self.assertContains(detail, "Add to watchlist")

    def test_search_matches_directors_and_clear_empty_state(self):
        response = self.client.get(reverse("search"), {"q": "A. Director"})
        self.assertEqual(response.context["page_obj"].paginator.count, 25)

        empty = self.client.get(reverse("search"), {"q": "no match"})
        self.assertContains(empty, "No matching films")

    def test_health_robots_and_sitemap_routes(self):
        self.assertEqual(self.client.get(reverse("healthz")).json(), {"status": "ok"})
        self.assertContains(self.client.get(reverse("robots")), "Sitemap:")
        self.assertContains(self.client.get(reverse("sitemap")), "/movie/1/")
