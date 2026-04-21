from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import EwastePin, AcceptedEwaste, Establishment, Freguesia, FavoritePoint, Locality

@admin.register(AcceptedEwaste)
class AcceptedEwasteAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')
    search_fields = ('type',)

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')
    search_fields = ('type',)

@admin.register(EwastePin)
class EwastePinAdmin(LeafletGeoAdmin):
    list_display = ('name', 'description','locality', 'types_of_establishment')
    list_filter = ('types_of_establishment', 'locality')
    search_fields = ('name', 'description', 'address', 'postal_code')
    
    filter_horizontal = ('accepted_ewaste',)

@admin.register(Freguesia)
class FreguesiaAdmin(LeafletGeoAdmin):
    list_display = ('nome', 'concelho', 'distrito')
    list_filter = ('concelho', 'distrito')
    search_fields = ('nome', 'concelho')

@admin.register(FavoritePoint)
class FavoritePointAdmin(admin.ModelAdmin):
    list_display = ('user', 'ewaste_pin', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'ewaste_pin__name', 'ewaste_pin__description')
    
@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)