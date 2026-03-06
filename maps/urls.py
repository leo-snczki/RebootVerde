from django.urls import path
from . import views

urlpatterns = [
    path("recycle-map/", views.recycle_map_view, name='maps'),
]