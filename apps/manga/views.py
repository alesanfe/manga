from django.shortcuts import render

from apps.manga.create_index import index_all_mangas
from apps.manga.populate_db import populate_mangas


# Create your views here.
def populate_db(request):
    print('Populating DB')
    # populate_mangas()
    index_all_mangas()
    return render(request, 'managa/populate_db.html')