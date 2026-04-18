import os
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, Polygon
from .models import Freguesia

shp_freguesias = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'gadm41_PRT_3', 'gadm41_PRT_3.shp')
)

def carregar_freguesias(verbose):
    if not os.path.exists(shp_freguesias):
        print(f"ERRO: Ficheiro não encontrado em: {shp_freguesias}")
        return
        
    print("\n--- A carregar Freguesias (Apenas Concelho de Lisboa) ---")
    ds = DataSource(shp_freguesias)
    layer = ds[0]

    freguesias_adicionadas = 0

    for feature in layer:
        if feature.get('NAME_2') == 'Lisboa':
            nome_freguesia = feature.get('NAME_3')
            concelho = feature.get('NAME_2')
            distrito = feature.get('NAME_1')
            
            geom = feature.geom.geos
            
            if isinstance(geom, Polygon):
                geom = MultiPolygon(geom)

            freguesia, created = Freguesia.objects.get_or_create(
                nome=nome_freguesia,
                concelho=concelho,
                distrito=distrito,
                defaults={'geom': geom}
            )

            if created:
                freguesias_adicionadas += 1
                if verbose:
                    print(f"Sucesso: Freguesia '{nome_freguesia}' adicionada!")

    print(f"Concluído! Foram adicionadas {freguesias_adicionadas} freguesias de Lisboa.")


def run(verbose=True):
    carregar_freguesias(verbose)