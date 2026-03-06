from django.contrib.gis.db import models

class PontoRecolha(models.Model):
    codigo_apa = models.CharField(max_length=50, null=True, blank=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    morada = models.CharField(max_length=255, null=True, blank=True)
    localidade = models.CharField(max_length=255, null=True, blank=True)
    codigo_pos = models.CharField(max_length=20, null=True, blank=True)
    
    geom = models.PointField(srid=4326)

    def __str__(self):
        return self.descricao or "Ponto de Recolha"