from django.contrib.gis.db import models
from django.conf import settings

class PontoRecolha(models.Model):
    codigo_apa = models.CharField(max_length=50, null=True, blank=True)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    morada = models.CharField(max_length=255, null=True, blank=True)
    localidade = models.CharField(max_length=255, null=True, blank=True)
    codigo_pos = models.CharField(max_length=20, null=True, blank=True)
    
    geom = models.PointField(srid=4326)

    def __str__(self):
        return self.descricao or "Ponto de Recolha"

class Freguesia(models.Model):
    nome = models.CharField(max_length=100)
    concelho = models.CharField(max_length=100)
    distrito = models.CharField(max_length=100)
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.nome
    
class FavoritePoint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_points'
    )
    ponto_recolha = models.ForeignKey(
        PontoRecolha,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ponto_recolha')
        verbose_name = 'Favorite Point'
        verbose_name_plural = 'Favorite Points'

    def __str__(self):
        return f"{self.user} - {self.ponto_recolha}"