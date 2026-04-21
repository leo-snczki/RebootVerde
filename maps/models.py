from django.contrib.gis.db import models
from django.conf import settings

class EwastePin(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    working_hours = models.CharField(max_length=255, null=True, blank=True)
    accepted_ewaste = models.ManyToManyField('AcceptedEwaste', blank=True)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    locality = models.ForeignKey('Locality', on_delete=models.CASCADE)
    types_of_establishment = models.ForeignKey('Establishment', on_delete=models.SET_NULL, null=True)
    official_link = models.URLField(max_length=255, null=True, blank=True)
    
    geom = models.PointField(srid=4326)

    def __str__(self):
        return self.name
    
class AcceptedEwaste(models.Model):
    type = models.CharField(max_length=255)
    
    def __str__(self):
        return self.type or "E-waste type"
    
class Establishment(models.Model):
    type = models.CharField(max_length=255)
    
    def __str__(self):
        return self.type or "Establishment type"
    
# bonzão para futuros upgrades sem ser em lisboa
class Locality(models.Model):
    name = models.CharField(max_length=30)
    
    class Meta:
        verbose_name = "Locality"
        verbose_name_plural = "Localities"
    
    def __str__(self):
        return self.name

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
    ewaste_pin = models.ForeignKey(
        EwastePin,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ewaste_pin')
        verbose_name = 'Favorite Point'
        verbose_name_plural = 'Favorite Points'

    def __str__(self):
        return f"{self.user} - {self.ewaste_pin}"