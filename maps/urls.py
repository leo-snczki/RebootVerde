from django.urls import path
from . import views

urlpatterns = [
    path("recycle-map/", views.recycle_map_view, name='maps'),
    path('api/eco-points/', views.api_pontos_geojson, name='points-api'),
]