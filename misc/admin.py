from django.contrib import admin

from utils.helpers import ModelAdmin

from .models import City, Province, Relationship


class CityAdmin(ModelAdmin):
    list_display = ["name", "province"]
    list_filter = [
        "province",
    ]
    search_fields = ["name", "province__name"]


class ProvinceAdmin(ModelAdmin):
    list_display = ["name", "abbreviation"]


class RelationshipAdmin(ModelAdmin):
    list_display = [
        "name",
    ]


admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Relationship, RelationshipAdmin)
