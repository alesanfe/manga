from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser

from apps.manga.models import Manga, Genre
from utils.db_populate import populate_mangas
from utils.index_creator import index_all_mangas
# Import centralized logger configuration
from utils.logger_config import logger
from utils.manga_services import get_soup, extract_chapters, download_chapter_images


# Create your views here.
def populate_db(request):
    """
    Puebla la base de datos con datos de manga y crea el índice de búsqueda.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponseRedirect a list_all_mangas
    """
    populate_mangas()
    index_all_mangas()
    return redirect('list_all_mangas')


def list_all_mangas(request):
    """
    Lista todos los mangas con filtros de búsqueda usando Whoosh.
    
    Filtros disponibles:
    - title: Filtro por título
    - genre: Filtro por género (múltiple)
    - author: Filtro por autor
    - start_year: Año de inicio
    - end_year: Año de fin
    
    Args:
        request: HttpRequest object con parámetros GET de filtros
        
    Returns:
        HttpResponse con la página list_all_mangas.html
    """
    # Abre el índice
    index = open_dir(settings.WHOOSH_INDEX_PATH)

    # Filtros
    title_filter = request.GET.get('title')
    genre_filter = request.GET.getlist('genre')  # Ahora obtiene una lista de géneros
    author_filter = request.GET.get('author')
    start_year_filter = request.GET.get('start_year')
    end_year_filter = request.GET.get('end_year')
    status_filter = request.GET.get('status')
    min_chapters_filter = request.GET.get('min_chapters')
    max_chapters_filter = request.GET.get('max_chapters')

    # Crea un analizador de consultas para los campos relevantes
    parser = MultifieldParser(["title", "author_name", "genres"], index.schema)

    # Construye la consulta
    query_parts = []

    if title_filter:
        query_parts.append(f"title:{title_filter}")
    if genre_filter and len(genre_filter) > 0 and genre_filter[0] != "":
        genre_query = " OR ".join(f"genres:{genre}" for genre in genre_filter)
        query_parts.append(f"({genre_query})")
    if author_filter:
        query_parts.append(f"author_name:{author_filter}")
    if start_year_filter:
        query_parts.append(f"release_year:[{start_year_filter} TO 3000]")
    if end_year_filter:
        query_parts.append(f"release_year:[0000 TO {end_year_filter}]")
    if status_filter:
        query_parts.append(f"status:{status_filter}")
    if min_chapters_filter:
        query_parts.append(f"num_caps:[{min_chapters_filter} TO 100000]")
    if max_chapters_filter:
        query_parts.append(f"num_caps:[0 TO {max_chapters_filter}]")

    # Si no se proporciona ningún filtro, incluir todos los mangas
    if not query_parts:
        query_parts.append("title:*")  # Filtro comodín que coincide con cualquier título

    logger.debug(f"Final Query: {' AND '.join(query_parts)}")
    query = parser.parse(" AND ".join(query_parts))

    # Realiza la búsqueda
    with index.searcher() as searcher:
        results = searcher.search(query, limit=None)  # Muestra 12 mangas por página
        # Convierte los resultados en mangas
        mangas_list = [Manga.objects.filter(title=result["title"]).first() for result in results if Manga.objects.filter(title=result["title"]).exists()]

    paginator = Paginator(mangas_list, 12)  # Muestra 10 mangas por página

    page = request.GET.get('page')
    try:
        mangas = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, entrega la primera página
        mangas = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera del rango (por ejemplo, 9999), entrega la última página
        mangas = paginator.page(paginator.num_pages)

    names_genres = Genre.objects.all().values_list('name', flat=True)

    # Pass current filter values to template for pagination
    context = {
        'mangas': mangas,
        'genres': names_genres,
        'current_filters': {
            'title': title_filter,
            'genres': genre_filter,
            'author': author_filter,
            'start_year': start_year_filter,
            'end_year': end_year_filter,
            'status': status_filter,
            'min_chapters': min_chapters_filter,
            'max_chapters': max_chapters_filter,
        }
    }

    return render(request, 'manga/list_all_mangas.html', context)


def find_manga(request, pk):
    """
    Muestra los detalles de un manga específico.
    
    Args:
        request: HttpRequest object
        pk: Primary key del manga
        
    Returns:
        HttpResponse con la página manga_details.html
    """
    manga = Manga.objects.get(pk=pk)
    logger.debug(f"Viewing manga: {manga.title}, chapters: {manga.num_caps}")
    return render(request, 'manga/manga_details.html', {'manga': manga})

def list_all_chapters(request, manga):
    """
    Lista todos los capítulos disponibles de un manga específico.

    Args:
        request: HttpRequest object
        manga: Nombre del manga en my.ninemanga.com

    Returns:
        HttpResponse con la página manga_chapters.html
    """
    logger.info(f"Starting to fetch chapters for manga: {manga}")
    url = f'https://my.ninemanga.com/manga/{manga}.html?waring=1'
    logger.debug(f"Fetching URL: {url}")

    try:
        soup = get_soup(url)
        logger.debug(f"Successfully fetched soup for manga: {manga}")

        dict_chapters = extract_chapters(soup)
        logger.info(soup)
        logger.info(f"Extracted {len(dict_chapters)} chapters for manga: {manga}")
        logger.debug(f"Chapters: {list(dict_chapters.keys())[:10]}")  # Log first 10 chapters

        return render(request, 'manga/manga_chapters.html', {'chapters': dict_chapters, 'manga': manga})
    except Exception as e:
        logger.error(f"Error fetching chapters for manga {manga}: {str(e)}", exc_info=True)
        raise


def view_chapter(request, manga, chapter):
    """
    Muestra las imágenes de un capítulo específico para leerlo en línea.

    Args:
        request: HttpRequest object
        manga: Nombre del manga en my.ninemanga.com
        chapter: Nombre del capítulo

    Returns:
        HttpResponse con la página view_chapter.html
    """
    logger.info(f"Starting to view chapter: {manga} - {chapter}")
    url = f'https://my.ninemanga.com/manga/{manga}.html?waring=1'

    try:
        soup = get_soup(url)
        chapter_links = extract_chapters(soup)

        # Find the chapter link that matches the requested chapter
        chapter_link = None
        current_chapter_num = None
        sorted_chapters = sorted(chapter_links.keys(), reverse=True)

        for title in sorted_chapters:
            if chapter in str(title):
                chapter_link = {title: chapter_links[title]}
                current_chapter_num = title
                break

        if not chapter_link:
            logger.error(f"Chapter not found: {chapter}")
            return render(request, 'manga/view_chapter.html', {'error': 'Capítulo no encontrado', 'manga': manga, 'chapter': chapter})

        # Calculate previous and next chapters
        current_index = sorted_chapters.index(current_chapter_num)
        previous_chapter = sorted_chapters[current_index + 1] if current_index + 1 < len(sorted_chapters) else None
        next_chapter = sorted_chapters[current_index - 1] if current_index - 1 >= 0 else None

        # Download images for the chapter
        images = download_chapter_images(chapter_link)
        logger.info(f"Downloaded {len(images)} images for chapter: {chapter}")

        return render(request, 'manga/view_chapter.html', {
            'images': images,
            'manga': manga,
            'chapter': chapter,
            'previous_chapter': previous_chapter,
            'next_chapter': next_chapter
        })
    except Exception as e:
        logger.error(f"Error viewing chapter {chapter} for manga {manga}: {str(e)}", exc_info=True)
        return render(request, 'manga/view_chapter.html', {'error': str(e), 'manga': manga, 'chapter': chapter})

