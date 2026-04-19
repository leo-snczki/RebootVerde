from django.urls import path
from . import views

urlpatterns = [
    path("recycle-map/", views.recycle_map_view, name='maps'),
    path('api/eco-points/', views.api_pins_geojson, name='points-api'),
    path('api/toggle-favorite/<int:point_id>/', views.toggle_favorite, name='toggle-favorite'),
]