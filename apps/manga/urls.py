from django.urls import path

from apps.manga import views, api

urlpatterns = [
    path('populate', views.populate_db, name='populate'),
    path('list_all_mangas', views.list_all_mangas, name='list_all_mangas'),
    path('details/<int:pk>', views.find_manga, name='find_manga'),
    path('download', api.MangaDownloadView.as_view(), name='download_manga'),
]