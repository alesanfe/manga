import logging
import os
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from django.db import transaction

from apps.manga.models import Author, Genre, Manga

logging.basicConfig(level=logging.INFO)

BASE_URL = 'https://my.ninemanga.com/category/index_{}.html'
MAX_PAGES = 100


def clean_database():
    """
    Cleans the database by deleting all records from the Author, Genre, and Manga models.
    """
    Author.objects.all().delete()
    Genre.objects.all().delete()
    Manga.objects.all().delete()
    for file in os.listdir('apps/static/assets/img'):
        if file.startswith('Manga -'):
            os.remove(os.path.join('apps/static/assets/img', file))



def create_unknown_author():
    """
    Creates or retrieves the 'Unknown' author from the database.

    Returns:
        Author: The 'Unknown' author instance.
    """
    unknown_author, created_author = Author.objects.get_or_create(name='Unknown')
    return unknown_author


def create_unknown_genre():
    """
    Creates or retrieves the 'Unknown' genre from the database.

    Returns:
        Genre: The 'Unknown' genre instance.
    """
    unknown_genre, created_genre = Genre.objects.get_or_create(name='Unknown')
    return unknown_genre


def get_or_create_author(name_author, all_authors, unknown_author):
    """
    Retrieves or creates an author instance based on the provided name.

    Parameters:
        name_author (Tag): BeautifulSoup Tag representing the author name.
        all_authors (Dict[str, Author]): Dictionary to cache already created authors.
        unknown_author (Author): The 'Unknown' author instance.

    Returns:
        Author: The author instance.
    """
    if name_author:
        name_author = name_author.find_next('a').text.strip()
        author = all_authors.setdefault(name_author, Author(name=name_author))
        if not author.pk:
            author.save()
            all_authors[name_author] = author
    else:
        author = unknown_author
    return author


def get_or_create_genres(names_genres, all_genres, unknown_genre):
    """
    Retrieves or creates genre instances based on the provided genre names.

    Parameters:
        names_genres (Tag): BeautifulSoup Tag representing the genre names.
        all_genres (Dict[str, Genre]): Dictionary to cache already created genres.
        unknown_genre (Genre): The 'Unknown' genre instance.

    Returns:
        List[Genre]: List of genre instances.
    """
    genres = []
    if names_genres:
        names_genres = [genre.text for genre in names_genres.find_all('a')]
        for name_genre in names_genres:
            genre = all_genres.setdefault(name_genre, Genre(name=name_genre))
            if not genre.pk:
                genre.save()
                all_genres[name_genre] = genre
            genres.append(genre)
    else:
        genres.append(unknown_genre)
    return genres


def create_and_save_manga(title, author, release_year, image_link, details_link, num_caps, views, genres):
    """
    Creates and saves a Manga instance.

    Parameters:
        title (str): The title of the manga.
        author (Author): The author instance.
        release_year (int): The release year of the manga.
        image_link (str): The link to the manga's cover image.
        details_link (str): The link to the details page of the manga.
        num_caps (int): The number of chapters in the manga.
        views (int): The number of views the manga has.
        genres (List[Genre]): List of genre instances.
    """
    m = Manga(
        title=title,
        author=author,
        release_year=release_year,
        image_link=image_link,
        details_link=details_link,
        num_caps=num_caps,
        views=views
    )
    m.save()
    m.genres.set(genres)
    logging.info(
        f"Title: {title}, Author: {author.name}, Release Year: {release_year}, Image Link: {image_link}, Details Link: {details_link}"
    )


@transaction.atomic
def populate_mangas():
    """
    Populates the database with manga information by scraping pages from the BASE_URL.
    """
    clean_database()
    unknown_author = create_unknown_author()
    unknown_genre = create_unknown_genre()

    all_authors = {}
    all_genres = {}

    with requests.Session() as session:
        for page in range(1, MAX_PAGES + 1):
            process_page(page, all_authors, all_genres, unknown_author, unknown_genre, session)


def process_page(page, all_authors, all_genres, unknown_author, unknown_genre, session):
    """
    Processes a page from the BASE_URL, scraping manga information and saving it to the database.

    Parameters:
        page (int): The page number.
        all_authors (Dict[str, Author]): Dictionary to cache already created authors.
        all_genres (Dict[str, Genre]): Dictionary to cache already created genres.
        unknown_author (Author): The 'Unknown' author instance.
        unknown_genre (Genre): The 'Unknown' genre instance.
        session: The requests session.
    """
    try:
        url = BASE_URL.format(page)
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        mangas = soup.find('ul', class_='direlist').find_all('dl', 'bookinfo')

        for manga in mangas:
            process_manga(manga, all_authors, all_genres, unknown_author, unknown_genre, session)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la página {page}: {str(e)}")


def process_manga(manga, all_authors, all_genres, unknown_author, unknown_genre, session):
    """
    Processes a manga from the BASE_URL, scraping its details and saving it to the database.

    Parameters:
        manga: The BeautifulSoup Tag representing the manga information.
        all_authors (Dict[str, Author]): Dictionary to cache already created authors.
        all_genres (Dict[str, Genre]): Dictionary to cache already created genres.
        unknown_author (Author): The 'Unknown' author instance.
        unknown_genre (Genre): The 'Unknown' genre instance.
        session: The requests session.
    """
    title = manga.find('a', class_='bookname').text
    details_link = manga.find('a', class_='bookname')['href']
    image_link = manga.find('img')['src']
    image_content = BytesIO(requests.get(image_link).content)
    save_title = title.replace('/', '_')
    file = f'apps/static/assets/img/Manga - {save_title}.png'
    # Guarda la imagen como png en la carpeta data
    with open(file, 'wb') as f:
        f.write(image_content.getvalue())


    views = int(manga.find('span').text.replace('views', '').replace(',', '').strip())

    details_response = session.get(details_link + "?waring=1")
    details_response.raise_for_status()
    details_soup = BeautifulSoup(details_response.text, 'lxml')
    name_author = details_soup.find('b', string='Autor(s):')
    release_year = details_soup.find('b', string='Año')

    release_year = int(release_year.find_next('a').text) if release_year else None

    names_genres = details_soup.find('li', itemprop='genre')
    sections = details_soup.find_all('ul', class_='sub_vol_ul')
    caps = [cap for section in sections for cap in section.find_all('a')]
    num_caps = len(caps)

    author = get_or_create_author(name_author, all_authors, unknown_author)
    genres = get_or_create_genres(names_genres, all_genres, unknown_genre)

    create_and_save_manga(title, author, release_year, file.replace('apps/static/assets/', ''), details_link, num_caps, views, genres)







