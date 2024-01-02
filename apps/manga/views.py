from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from apps.manga.create_index import index_all_mangas
from apps.manga.models import Manga
from apps.manga.populate_db import populate_mangas


# Create your views here.
def populate_db(request):
    populate_mangas()
    index_all_mangas()
    return render(request, 'manga/populate_db.html')

def list_all_mangas(request):
    mangas_list = Manga.objects.all()
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

    return render(request, 'manga/list_all_mangas.html', {'mangas': mangas})

def find_manga(request, pk):
    print(Manga.objects.get(pk=pk).num_caps)
    return render(request, 'manga/manga_details.html', {'manga': Manga.objects.get(pk=pk)})
