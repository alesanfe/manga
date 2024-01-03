import logging
import os
from contextlib import closing

from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD
from whoosh.index import create_in
from whoosh.writing import AsyncWriter

from apps.manga.models import Manga

logging.basicConfig(level=logging.INFO)

# Constants
INDEX_PATH = "data/index"
manga_schema = Schema(
    title=TEXT(stored=True),
    author_name=TEXT(stored=True),
    release_year=NUMERIC(stored=True),
    genres=KEYWORD(stored=True, commas=True),
)


def create_whoosh_index(index_path=INDEX_PATH):
    """
    Create or open a Whoosh index for manga.

    Parameters:
        index_path (str, optional): The path to the directory where the index will be stored. Defaults to "data/index".

    Returns:
        whoosh.index.Index: The created or opened Whoosh index.
    """
    if not os.path.exists(index_path):
        os.makedirs(index_path)
    return create_in(index_path, manga_schema)


def index_manga(writer, manga):
    """
    Index manga information into the Whoosh index.

    Parameters:
        writer (whoosh.writing.AsyncWriter): The Whoosh AsyncWriter instance.
        manga (apps.manga.models.Manga): The Manga object to be indexed.

    Returns:
        None
    """
    try:
        writer.add_document(
            title=manga.title,
            author_name=manga.author.name,
            release_year=manga.release_year,
            genres=", ".join(genre.name for genre in manga.genres.all()),
        )
        logging.info(f"Indexed {manga.title}")
    except Exception as e:
        logging.error(f"Error indexing {manga.title}: {e}")


def index_all_mangas(index_path=INDEX_PATH):
    """
    Index all manga information from the database into the Whoosh index.

    Parameters:
        index_path (str, optional): The path to the directory where the index will be stored. Defaults to "data/index".

    Returns:
        None
    """
    ix = create_whoosh_index(index_path)
    writer = ix.writer()
    try:
        # Obtain all manga from the database
        mangas = Manga.objects.all()

        for manga in mangas:
            index_manga(writer, manga)

        # Commit at the end of indexing
        writer.commit()
    except Exception as e:
        logging.error(f"Error during indexing: {e}")
    finally:
        ix.close()
