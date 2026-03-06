from django.shortcuts import render
from django.core.serializers import serialize
from .models import PontoRecolha

def recycle_map_view(request):
    pontos = PontoRecolha.objects.filter(localidade="Lisboa")[:500]
    pontos_geojson = serialize('geojson', pontos, geometry_field='geom', fields=('descricao', 'morada', 'localidade'))
    
    return render(request, 'maps/recycle_map.html', {
        'pontos_geojson': pontos_geojson
    })