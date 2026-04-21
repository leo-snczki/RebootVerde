from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name='index'),
    path("about/", views.about, name='about'),
    path("play/", views.game_view, name='game'),
    path("contact/", views.contact_view, name='contact'),
    path('learn/', views.learn, name='learn'),
    path('statistics/', views.statistics_view, name='statistics'),
]