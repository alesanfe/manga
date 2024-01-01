from django.urls import path

from apps.manga import views

urlpatterns = [
    path('populate', views.populate_db, name='populate')

]