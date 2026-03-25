from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_active', 'is_special')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)