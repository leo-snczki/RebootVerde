from django.shortcuts import render
from django.core.serializers import serialize
from .models import PontoRecolha, Freguesia
import json
from django.http import JsonResponse
from django.db.models import Q

BRANDS_REEE = ["Minipreço", "ALDI", "Minisom", "Fnac", "Primark", "Pingo Doce", "Canon", "Konica", "Nintendo", "Cepsa", "Worten", "Staples", "El Corte Inglês", "Decathlon", "Leroy Merlin", "Auchan", "Junta de Freguesia", "Hotel", "Lidl", "ALE-HOP" ] # dps coloco mais

CIVIL_PARISHES = ["Ajuda", "Alcântara", "Alvalade", "Arreiro", "Arroios", "Avenidas Novas", "Beato", "Belém", "Benfica", "Campo de Ourique", "Campolide", "Carnide", "Estrela", "Lumiar", "Marvila", "Misericórdia", "Olivais", "Parque das Nações", "Penha de França", "Santa Clara", "Santa Maria Maior", "Santo António", "São Domingos de Benfica", "São Vicente"]
def recycle_map_view(request):
    return render(request, 'maps/recycle_map.html', {
        'brands': BRANDS_REEE,
        'parishes': CIVIL_PARISHES
    })

def api_pins_geojson(request):
    selected_brands = request.GET.getlist('brand')
    search = request.GET.get('search')
    selected_parishes = request.GET.getlist('parish')

    pins = PontoRecolha.objects.filter(localidade__iexact="lisboa")

    if search:
        pins = pins.filter(descricao__icontains=search)

    if selected_brands:
        brand_filter = Q()
        for brand in selected_brands:
            brand_filter |= Q(descricao__icontains=brand)
        
        pins = pins.filter(brand_filter)

    if selected_parishes:
        freguesias_selecionadas = Freguesia.objects.filter(
            concelho='Lisboa', 
            nome__in=selected_parishes
        )
        
        if freguesias_selecionadas.exists():
            parish_filter = Q()
            for freguesia in freguesias_selecionadas:
                parish_filter |= Q(geom__within=freguesia.geom)
            
            pins = pins.filter(parish_filter)
        else:
            pins = pins.none()
            
    geojson_data = serialize(
        'geojson', 
        pins[:500], # tem 475 em lisboa mas ok
        geometry_field='geom',
        fields=('descricao', 'morada', 'localidade')
    )
    
    return JsonResponse(json.loads(geojson_data))