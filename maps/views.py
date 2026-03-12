from django.shortcuts import render
from django.core.serializers import serialize
from .models import PontoRecolha
import json
from django.http import JsonResponse

BRANDS_REEE = ["Minipreço", "ALDI", "Minisom", "Fnac"] # dps coloco mais

def recycle_map_view(request):
    return render(request, 'maps/recycle_map.html', {
        'brands': BRANDS_REEE
    })

def api_pontos_geojson(request):
    
    brand_selecionada = request.GET.get('brand')
    
    pontos = PontoRecolha.objects.filter(localidade="Lisboa")

    if brand_selecionada in BRANDS_REEE:
        pontos = pontos.filter(descricao__icontains=brand_selecionada)
    
    
    geojson_data = serialize(
        'geojson', 
        pontos[:500], # tem 475 em lisboa mas ok
        geometry_field='geom',
        fields=('descricao', 'morada', 'localidade')
    )
    
    return JsonResponse(json.loads(geojson_data))