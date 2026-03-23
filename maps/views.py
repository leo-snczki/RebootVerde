from django.shortcuts import render
from django.core.serializers import serialize
from .models import PontoRecolha, Freguesia
import json
from django.http import JsonResponse
from django.db.models import Q

BRANDS_REEE = ["Minipreço", "ALDI", "Minisom", "Fnac", "Primark", "Pingo Doce", "Canon", "Konica", "Nintendo", "Cepsa", "Worten", "Staples", "El Corte Inglês", "Decathlon", "Leroy Merlin", "Auchan", "Junta de Freguesia", "Hotel", "Lidl", "ALE-HOP" ] # dps coloco mais

CIVIL_PARISHES = [
    "Ajuda", "Alcântara", "Alto Do Pina", "Alvalade", "Ameixoeira", "Anjos", 
    "Beato", "Benfica", "Campo Grande", "Campolide", "Carnide", "Castelo", 
    "Charneca", "Coração De Jesus", "Encarnação", "Graça", "Lapa", "Lumiar", 
    "Madalena", "Mártires", "Marvila", "Mercês", "Nossa Senhora De Fátima", 
    "Pena", "Penha De França", "Prazeres", "Sacramento", "Santa Catarina", 
    "Santa Engrácia", "Santa Isabel", "Santa Justa", "Santa Maria De Belém", 
    "Santa Maria Dos Olivais", "Santiago", "Santo Condestável", "Santo Estêvão", 
    "Santos-O-Velho", "São Cristóvão E São Lourenço", "São Domingos De Benfica", 
    "São Francisco Xavier", "São João", "São João De Brito", "São João De Deus", 
    "São Jorge De Arroios", "São José", "São Mamede", "São Miguel", "São Nicolau", 
    "São Paulo", "São Sebastião Da Pedreira", "São Vicente De Fora", "Sé", "Socorro"
]

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
        pins[:500], # tem 1200 na vdd, mas para evitar sobrecarregar o browser, 500 serve
        geometry_field='geom',
        fields=('descricao', 'morada', 'localidade', 'codigo_pos')
    )
    
    return JsonResponse(json.loads(geojson_data))