from django.contrib import admin
from .models import Texto

@admin.register(Texto)
class TextoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'template')
    search_fields = ('titulo',)