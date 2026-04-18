import os
from django.contrib.gis.utils import LayerMapping
from .models import PontoRecolha

mapping = {
    'codigo_apa': 'codigo_apa',
    'descricao': 'descricao',
    'morada': 'morada',
    'localidade': 'localidade',
    'codigo_pos': 'codigo_pos',
    'geom': 'POINT',
}

shp_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'd306_ponto_recolha_eletronicos_pub_vw', 'd306_ponto_recolha_eletronicos_pub_vw.shp')
)

def run(verbose=True):
    if not os.path.exists(shp_file):
        print(f"ERRO: Ficheiro não encontrado em: {shp_file}")
        return

    lm = LayerMapping(PontoRecolha, shp_file, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)