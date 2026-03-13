from django.shortcuts import render
from django.core.serializers import serialize
from .models import PontoRecolha
import json
from django.http import JsonResponse
from django.db.models import Q

BRANDS_REEE = ["Minipreço", "ALDI", "Minisom", "Fnac", "Primark", "Pingo Doce", "Canon", "Konica", "Nintendo", "Cepsa", "Worten", "Staples", "El Corte Inglês", "Decathlon", "Leroy Merlin", "Auchan", "Junta de Freguesia", "Hotel", "Lidl", "ALE-HOP" ] # dps coloco mais

def recycle_map_view(request):
    return render(request, 'maps/recycle_map.html', {
        'brands': BRANDS_REEE
    })

def api_pins_geojson(request):
    selected_brandscionadas = request.GET.getlist('brand')
    
    pins = PontoRecolha.objects.filter(localidade__iexact="lisboa")

    # Se houver marcas selecionadas, construímos uma consulta dinâmica
    # Usamos o objeto Q para acumular filtros com o 'OR'
    if selected_brandscionadas:
        brand_filter = Q()
        
        for brand in selected_brandscionadas:
            brand_filter |= Q(descricao__icontains=brand)
        
        pins = pins.filter(brand_filter)
    
    geojson_data = serialize(
        'geojson', 
        pins[:500], # tem 475 em lisboa mas ok
        geometry_field='geom',
        fields=('descricao', 'morada', 'localidade')
    )
    
    return JsonResponse(json.loads(geojson_data))