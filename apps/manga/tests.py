from django.contrib.auth.models import User
from django.test import TestCase

from apps.manga.models import Author, Genre, Manga, Score


class AuthorModelTest(TestCase):
    def setUp(self):
        Author.objects.create(name="Test Author")

    def test_author_str(self):
        author = Author.objects.get(name="Test Author")
        self.assertEqual(str(author), "Test Author")


class GenreModelTest(TestCase):
    def setUp(self):
        Genre.objects.create(name="Action")

    def test_genre_str(self):
        genre = Genre.objects.get(name="Action")
        self.assertEqual(str(genre), "Action")


class MangaModelTest(TestCase):
    def setUp(self):
        author = Author.objects.create(name="Test Author")
        genre = Genre.objects.create(name="Action")
        manga = Manga.objects.create(
            title="Test Manga",
            author=author,
            release_year=2020,
            image_link="http://example.com/image.jpg",
            details_link="http://example.com/details",
            num_caps=100,
            views=1000
        )
        manga.genres.add(genre)

    def test_manga_str(self):
        manga = Manga.objects.get(title="Test Manga")
        self.assertEqual(str(manga), "Test Manga")

    def test_manga_fields(self):
        manga = Manga.objects.get(title="Test Manga")
        self.assertEqual(manga.release_year, 2020)
        self.assertEqual(manga.num_caps, 100)
        self.assertEqual(manga.views, 1000)


class ScoreModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        author = Author.objects.create(name="Test Author")
        manga = Manga.objects.create(
            title="Test Manga",
            author=author,
            release_year=2020,
            image_link="http://example.com/image.jpg",
            details_link="http://example.com/details",
            num_caps=100,
            views=1000
        )
        Score.objects.create(manga=manga, user=user, score=8.5)

    def test_score_str(self):
        score = Score.objects.get(score=8.5)
        self.assertEqual(str(score), "8.5")

    def test_score_unique_constraint(self):
        user = User.objects.get(username="testuser")
        manga = Manga.objects.get(title="Test Manga")
        # Intentar crear otro score para el mismo usuario y manga debería fallar
        with self.assertRaises(Exception):
            Score.objects.create(manga=manga, user=user, score=9.0)
