from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from django.contrib.auth import get_user_model
from .models import EwastePin, AcceptedEwaste, Establishment, Freguesia, FavoritePoint, Locality, EwastePinOpeningHours, RecyclingCode, RedemptionLog
from django.db.models import Q

User = get_user_model()

@admin.register(AcceptedEwaste)
class AcceptedEwasteAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')
    search_fields = ('type',)

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')
    search_fields = ('type',)

class EwastePinOpeningHoursInline(admin.TabularInline):
    model = EwastePinOpeningHours
    extra = 1
    min_num = 0

@admin.register(EwastePin)
class EwastePinAdmin(LeafletGeoAdmin):
    list_display = ('name', 'description','locality', 'types_of_establishment')
    list_filter = ('types_of_establishment', 'locality')
    search_fields = ('name', 'description', 'address', 'postal_code')
    
    filter_horizontal = ('accepted_ewaste',)
    
    inlines = [EwastePinOpeningHoursInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="Owner").exists():
            return qs.filter(owner=request.user)
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            if request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(
                    Q(is_staff=True) | Q(groups__name="Owner")
                ).distinct()

            elif request.user.groups.filter(name="Owner").exists():
                kwargs["queryset"] = User.objects.filter(groups__name="Owner")

            else:
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj and obj.owner != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj and obj.owner != request.user:
            return False
        return True

@admin.register(Freguesia)
class FreguesiaAdmin(LeafletGeoAdmin):
    list_display = ('nome', 'concelho', 'distrito')
    list_filter = ('concelho', 'distrito')
    search_fields = ('nome', 'concelho')

@admin.register(FavoritePoint)
class FavoritePointAdmin(admin.ModelAdmin):
    list_display = ('user', 'ewaste_pin', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'ewaste_pin__name', 'ewaste_pin__description')
    
@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(RecyclingCode)
class RecyclingCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "created_by", "points", "is_used")

    readonly_fields = (
        "code",
        "created_by",
        "points",
        "is_used",
        "used_by",
        "used_at",
        "created_at",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ewaste_pin":
            if request.user.groups.filter(name="Owner").exists():
                kwargs["queryset"] = EwastePin.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="Owner").exists():
            return qs.filter(created_by=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(RedemptionLog)