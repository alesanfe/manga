import os
import random
import time
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from django.db import transaction

from apps.manga.models import Author, Genre, Manga
# Import centralized logger configuration
from utils.logger_config import logger
# Import Chrome driver context manager
from utils.selenium_driver import ChromeDriverContext

BASE_URL = 'https://my.ninemanga.com/category/index_{}.html'
MAX_PAGES = 1

def clean_database():
    """
    Cleans the database by deleting all records from the Author, Genre, and Manga models.
    """
    Author.objects.all().delete()
    Genre.objects.all().delete()
    Manga.objects.all().delete()
    img_dir = 'static/assets/img'
    if os.path.exists(img_dir):
        for file in os.listdir(img_dir):
            if file.startswith('Manga -'):
                os.remove(os.path.join(img_dir, file))



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


def create_and_save_manga(title, alternative_titles, author, release_year, status, image_link, details_link, description, num_caps, views, likes, genres):
    """
    Creates and saves a Manga instance.

    Parameters:
        title (str): The title of the manga.
        alternative_titles (str): Alternative titles of the manga.
        author (Author): The author instance.
        release_year (int): The release year of the manga.
        status (str): The status of the manga.
        image_link (str): The link to the manga's cover image.
        details_link (str): The link to the details page of the manga.
        description (str): The description/summary of the manga.
        num_caps (int): The number of chapters in the manga.
        views (int): The number of views the manga has.
        likes (int): The number of likes the manga has.
        genres (List[Genre]): List of genre instances.
    """
    m = Manga(
        title=title,
        alternative_titles=alternative_titles,
        author=author,
        release_year=release_year,
        status=status,
        image_link=image_link,
        details_link=details_link,
        description=description,
        num_caps=num_caps,
        views=views,
        likes=likes
    )
    m.save()
    m.genres.set(genres)
    logger.info(
        f"Title: {title}, Author: {author.name}, Status: {status}, Release Year: {release_year}, Image Link: {image_link}, Details Link: {details_link}"
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

    with ChromeDriverContext() as driver:
        for page in range(1, MAX_PAGES + 1):
            process_page(page, all_authors, all_genres, unknown_author, unknown_genre, driver)

    # Fix image paths after populating
    fix_image_paths()


def process_page(page, all_authors, all_genres, unknown_author, unknown_genre, driver):
    """
    Processes a page from the BASE_URL, scraping manga information and saving it to the database.

    Parameters:
        page (int): The page number.
        all_authors (Dict[str, Author]): Dictionary to cache already created authors.
        all_genres (Dict[str, Genre]): Dictionary to cache already created genres.
        unknown_author (Author): The 'Unknown' author instance.
        unknown_genre (Genre): The 'Unknown' genre instance.
        driver: The Selenium WebDriver instance.
    """
    try:
        url = BASE_URL.format(page)
        driver.get(url)
        page_source = driver.page_source
        
        # Check if Cloudflare blocked the request
        if 'Cloudflare' in page_source or 'Attention Required!' in page_source or 'you have been blocked' in page_source.lower():
            logger.error(f"Cloudflare blocked page {page} at {url}")
            return
        
        soup = BeautifulSoup(page_source, 'lxml')
        logger.info(f"Processing page {page} with URL: {url}")
        
        direlist = soup.find('ul', class_='direlist')
        if not direlist:
            logger.error(f"Could not find 'direlist' element on page {page}")
            return
        
        mangas = direlist.find_all('dl', 'bookinfo')

        # Process mangas sequentially for SQLite compatibility
        for manga in mangas:
            process_manga(manga, all_authors, all_genres, unknown_author, unknown_genre, driver)

    except Exception as e:
        logger.error(f"Error en la página {page}: {str(e)}")


def process_manga(manga, all_authors, all_genres, unknown_author, unknown_genre, driver):
    """
    Processes a manga from the BASE_URL, scraping its details and saving it to the database.

    Parameters:
        manga: The BeautifulSoup Tag representing the manga information.
        all_authors (Dict[str, Author]): Dictionary to cache already created authors.
        all_genres (Dict[str, Genre]): Dictionary to cache already created genres.
        unknown_author (Author): The 'Unknown' author instance.
        unknown_genre (Genre): The 'Unknown' genre instance.
        driver: The Selenium WebDriver instance.
    """
    title = manga.find('a', class_='bookname').text
    details_link = manga.find('a', class_='bookname')['href']
    image_link = manga.find('img')['src']
    # Increased delay before downloading image
    time.sleep(random.uniform(1, 2))
    
    save_title = title.replace('/', '_')
    # Ensure directory exists
    os.makedirs('static/assets/img', exist_ok=True)
    
    # Check if image_link already has an extension
    extension = ''
    if '.' in image_link.split('/')[-1]:
        # URL already has an extension, extract it
        extension = '.' + image_link.split('/')[-1].split('.')[-1]
    else:
        # No extension, add .png
        extension = '.png'
    
    file = f'static/assets/img/Manga - {save_title}{extension}'
    
    try:
        image_response = requests.get(image_link, timeout=10)
        image_response.raise_for_status()
        image_content = BytesIO(image_response.content)
        
        # Save image if successfully downloaded
        with open(file, 'wb') as f:
            f.write(image_content.getvalue())
            
    except Exception as e:
        logger.warning(f"Failed to download image for {title}: {str(e)}")

    span = manga.find('span')
    if span:
        views = int(span.text.replace('views', '').replace(',', '').strip())
    else:
        views = 0  # Default value if span is not found

    try:
        driver.get(details_link + "?waring=1")
        page_source = driver.page_source
        
        # Check if Cloudflare blocked the request
        if 'Cloudflare' in page_source or 'Attention Required!' in page_source or 'you have been blocked' in page_source.lower():
            logger.warning(f"Cloudflare blocked request for {title} at {details_link}")
            # Use default values when blocked
            author = unknown_author
            genres = [unknown_genre]
            release_year = None
            num_caps = 0
            create_and_save_manga(title, None, author, release_year, 'unknown', file.replace('static/', ''), details_link, None, num_caps, views, 0, genres)
            return
        
        details_soup = BeautifulSoup(page_source, 'lxml')
        logger.info(f"Getting details for {title} from {details_link}")
        
        # Extract alternative titles
        alternative_titles_elem = details_soup.find('b', string='Alternativa(s):')
        alternative_titles = None
        if alternative_titles_elem:
            alt_titles_text = alternative_titles_elem.parent.get_text(strip=True)
            if 'Alternativa(s):' in alt_titles_text:
                alternative_titles = alt_titles_text.replace('Alternativa(s):', '').strip()

        # Extract description/summary
        description_elem = details_soup.find('p', itemprop='description')
        description = None
        if description_elem:
            description_text = description_elem.get_text(strip=True)
            if 'Resumen:' in description_text:
                description = description_text.replace('Resumen:', '').strip()

        # Extract status
        status_elem = details_soup.find('b', string='Estado:')
        status = 'unknown'
        if status_elem:
            status_text = status_elem.parent.get_text(strip=True)
            if 'Estado:' in status_text:
                status_text_clean = status_text.replace('Estado:', '').strip()
                if 'En curso' in status_text_clean:
                    status = 'ongoing'
                elif 'Completado' in status_text_clean or 'Completed' in status_text_clean:
                    status = 'completed'
                elif 'Pausado' in status_text_clean or 'Hiatus' in status_text_clean:
                    status = 'hiatus'
                elif 'Cancelado' in status_text_clean or 'Cancelled' in status_text_clean:
                    status = 'cancelled'
        
        # Extract likes (from the first like counter)
        likes_elem = details_soup.find('span', class_='stBubble_count')
        likes = 0
        if likes_elem:
            try:
                likes = int(likes_elem.text.strip())
            except ValueError:
                likes = 0
        
        name_author = details_soup.find('b', string='Autor(s):')
        release_year = details_soup.find('b', string='Año')

        release_year = int(release_year.find_next('a').text) if release_year else None

        names_genres = details_soup.find('li', itemprop='genre')
        sections = details_soup.find_all('ul', class_='sub_vol_ul')
        caps = [cap for section in sections for cap in section.find_all('a')]
        num_caps = len(caps)

        author = get_or_create_author(name_author, all_authors, unknown_author)
        genres = get_or_create_genres(names_genres, all_genres, unknown_genre)

        create_and_save_manga(title, alternative_titles, author, release_year, status, file.replace('static/', ''), details_link, description, num_caps, views, likes, genres)
    except Exception as e:
        logger.error(f"Failed to get details for {title}: {str(e)}")


def fix_image_paths():
    """
    Fix image paths in database to use relative paths without /static/ prefix.
    """
    count = 0
    for manga in Manga.objects.all():
        if manga.image_link.startswith('/static/'):
            manga.image_link = manga.image_link.replace('/static/', '', 1)
            manga.save()
            count += 1
        elif manga.image_link.startswith('img/'):
            # Change img/ to assets/img/default-avatar.png
            manga.image_link = 'assets/img/default-avatar.png'
            manga.save()
            count += 1
    logger.info(f"Fixed {count} image paths")







