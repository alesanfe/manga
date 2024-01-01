from django.contrib import admin
from .models import Author, Genre, Manga, Score

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Manga)
admin.site.register(Score)

