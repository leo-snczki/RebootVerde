from django.contrib.gis.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
from django.conf import settings

class EwastePin(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    accepted_ewaste = models.ManyToManyField('AcceptedEwaste', blank=True)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    locality = models.ForeignKey('Locality', on_delete=models.CASCADE)
    types_of_establishment = models.ForeignKey('Establishment', on_delete=models.SET_NULL, null=True)
    official_link = models.URLField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="ewaste_pins")
    
    geom = models.PointField(srid=4326)

    def __str__(self):
        return self.name
    
class AcceptedEwaste(models.Model):
    type = models.CharField(max_length=255)
    points = models.PositiveIntegerField(default=0)
    
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

class EwastePinOpeningHours(models.Model):
    WEEKDAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    ewaste_pin = models.ForeignKey(
        "EwastePin",
        on_delete=models.CASCADE,
        related_name="opening_hours"
    )

    weekday = models.IntegerField(choices=WEEKDAYS)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        ordering = ["weekday", "open_time"]
        unique_together = ('ewaste_pin', 'weekday')
        
    def clean(self):
        if self.open_time and self.close_time:
            if self.close_time <= self.open_time:
                raise ValidationError({
                    'close_time': "The closing time must be after the opening time."
                })

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

User = settings.AUTH_USER_MODEL

class RecyclingCode(models.Model):
    code = models.CharField(max_length=12, unique=True, editable=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    ewaste_pin = models.ForeignKey("EwastePin", on_delete=models.CASCADE)

    waste_type = models.ForeignKey(AcceptedEwaste, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    points = models.PositiveIntegerField()

    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="used_codes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:10].upper()

        if self.waste_type:
            self.points = self.waste_type.points * self.quantity

        super().save(*args, **kwargs)

    def __str__(self):
        return self.code


class RedemptionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.OneToOneField(RecyclingCode, on_delete=models.CASCADE)

    points_earned = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)    