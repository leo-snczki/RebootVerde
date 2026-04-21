from urllib import request

from django.shortcuts import render, get_object_or_404
from django.core.serializers import serialize
from .models import EwastePin, Establishment, AcceptedEwaste, Freguesia, FavoritePoint
import json
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

BRANDS_REEE = [
    "Minipreço", "Continente", "ALDI", "Minisom", "Fnac", "Primark", "Pingo Doce", "Canon", "Konica", "Nintendo", "Cepsa", "Worten",
    "Staples", "El Corte Inglês", "Decathlon", "Leroy Merlin", "Auchan", "Lidl", "ALE-HOP"
]

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
        'parishes': CIVIL_PARISHES,
        'categories': AcceptedEwaste.objects.all(),
        'establishments': Establishment.objects.all()
    })


def api_pins_geojson(request):
    selected_brands = request.GET.getlist('brand')
    search = request.GET.get('search')
    selected_parishes = request.GET.getlist('parish')
    selected_categories = request.GET.getlist('category')
    selected_establishments = request.GET.getlist('establishment')
    favorites_only = request.GET.get('favorites') == 'true'
    weekday = request.GET.get('weekday')
    open_from = request.GET.get('open_from')
    open_to = request.GET.get('open_to')

    pins = EwastePin.objects.filter(locality__name__iexact="lisboa")

    if favorites_only and request.user.is_authenticated:
        fav_ids = FavoritePoint.objects.filter(user=request.user).values_list('ewaste_pin_id', flat=True)
        pins = pins.filter(id__in=fav_ids)
    elif favorites_only and not request.user.is_authenticated:
        pins = pins.none()

    if selected_categories:
        pins = pins.filter(accepted_ewaste__type__in=selected_categories).distinct()
        
    if selected_establishments:
        pins = pins.filter(types_of_establishment__type__in=selected_establishments)

    if weekday or open_from or open_to:
        hours_filter = Q()
        if weekday:
            hours_filter &= Q(opening_hours__weekday=weekday)
        if open_from:
            hours_filter &= Q(opening_hours__open_time__lte=open_from)
        if open_to:
            hours_filter &= Q(opening_hours__close_time__gte=open_to)
        
        pins = pins.filter(hours_filter).distinct()

    if search:
        pins = pins.filter(name__icontains=search)

    if selected_brands:
        brand_filter = Q()
        for brand in selected_brands:
            brand_filter |= Q(name__icontains=brand)

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
        pins[:1200],
        geometry_field='geom',
        fields=('name', 'description', 'working_hours', 'accepted_ewaste', 'address', 'postal_code', 'types_of_establishment', 'official_link')
    )

    data = json.loads(geojson_data)

    if request.user.is_authenticated:
        fav_ids = set(FavoritePoint.objects.filter(user=request.user).values_list('ewaste_pin_id', flat=True))
    else:
        fav_ids = set()

    for feature in data['features']:
        feature['properties']['is_favorited'] = feature['id'] in fav_ids

    return JsonResponse(data)

@require_POST
def toggle_favorite(request, point_id):
    if not request.user.is_authenticated:
        messages.error(request, "Precisas de iniciar sessão para adicionar favoritos.")
        return JsonResponse({'error': 'auth'}, status=401)

    ponto = get_object_or_404(EwastePin, id=point_id)
    
    favorite, created = FavoritePoint.objects.get_or_create(user=request.user, ewaste_pin=ponto)

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'unfavorited'})

    return JsonResponse({'status': 'favorited'})

def api_pin_details(request, pin_id):
    pin = get_object_or_404(EwastePin, id=pin_id)
    
    # Buscar horários
    horarios = pin.opening_hours.all()
    horarios_data = [
        {
            'day': h.get_weekday_display(),
            'open': h.open_time.strftime('%H:%M'),
            'close': h.close_time.strftime('%H:%M')
        } for h in horarios
    ]
    
    # Buscar categorias (nomes)
    categorias = [cat.type for cat in pin.accepted_ewaste.all()]

    return JsonResponse({
        'name': pin.name,
        'description': pin.description,
        'address': pin.address,
        'postal_code': pin.postal_code,
        'official_link': pin.official_link,
        'accepted_ewaste': categorias,
        'opening_hours': horarios_data,
        'establishment': pin.types_of_establishment.type if pin.types_of_establishment else ""
    })