from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Producto

# 1. Definimos el recurso para saber qué datos mover
class ProductoResource(resources.ModelResource):
    class Meta:
        model = Producto
        # Asegúrate de que estos nombres coincidan con los de tu modelo Producto
        fields = ('id', 'name', 'description', 'price', 'category', 'is_active', 'is_special')

# 2. Registramos el modelo con la funcionalidad de Import/Export
@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    resource_class = ProductoResource
    list_display = ('name', 'price', 'category', 'is_active', 'is_special')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)