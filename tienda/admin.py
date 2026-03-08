from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "price", "is_active", "is_special", "created_at")
	list_filter = ("is_active", "is_special")
	search_fields = ("name",)
