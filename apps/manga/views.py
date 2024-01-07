from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from apps.manga.create_index import index_all_mangas
from apps.manga.downloader import get_soup, extract_chapters
from apps.manga.models import Manga, Genre
from apps.manga.populate_db import populate_mangas
from whoosh.qparser import MultifieldParser, GtLtPlugin
from whoosh.index import open_dir


# Create your views here.
def populate_db(request):
    populate_mangas()
    index_all_mangas()
    return render(request, 'manga/populate_db.html')


def list_all_mangas(request):
    # Abre el índice
    index = open_dir("data/index")

    # Filtros
    title_filter = request.GET.get('title')
    genre_filter = request.GET.getlist('genre')  # Ahora obtiene una lista de géneros
    author_filter = request.GET.get('author')
    start_year_filter = request.GET.get('start_year')
    end_year_filter = request.GET.get('end_year')

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

    # Si no se proporciona ningún filtro, incluir todos los mangas
    if not query_parts:
        query_parts.append("title:*")  # Filtro comodín que coincide con cualquier título

    print("Final Query:", " AND ".join(query_parts))
    query = parser.parse(" AND ".join(query_parts))

    # Realiza la búsqueda
    with index.searcher() as searcher:
        results = searcher.search(query, limit=None)  # Muestra 12 mangas por página
        # Convierte los resultados en mangas
        mangas_list = [Manga.objects.get(title=result["title"]) for result in results]

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

    return render(request, 'manga/list_all_mangas.html', {'mangas': mangas, 'genres': names_genres})

    # Realiza la búsqueda
    with index.searcher() as searcher:
        results = searcher.search_page(query, 1, pagelen=12)  # Muestra 12 mangas por página
        # Convierte los resultados en mangas
        mangas = [Manga.objects.get(title=result["title"]) for result in results]

    names_genres = Genre.objects.all().values_list('name', flat=True)

    return render(request, 'manga/list_all_mangas.html', {'mangas': mangas, 'genres': names_genres})


def find_manga(request, pk):
    print(Manga.objects.get(pk=pk).num_caps)
    return render(request, 'manga/manga_details.html', {'manga': Manga.objects.get(pk=pk)})

def list_all_chapters(request, manga):
    soup = get_soup(f'https://my.ninemanga.com/manga/{manga}.html?waring=1')
    dict_chapters = extract_chapters(soup)
    return render(request, 'manga/manga_chapters.html', {'chapters': dict_chapters, 'manga': manga})

