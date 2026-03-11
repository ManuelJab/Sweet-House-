from decimal import Decimal
from typing import Dict
from collections import defaultdict

from .models import Producto
from django.conf import settings


from django.db import connection, ProgrammingError

def cart_summary(request) -> Dict[str, object]:
    """Añade al contexto el número de ítems y el total del carrito."""

    # Valores por defecto en caso de error o base de datos no migrada
    default_context = {
        'cart_count': 0,
        'cart_total': Decimal('0.00'),
        'productos_por_categoria': {},
        'postres_especiales': []
    }

    # Verificar si la tabla de productos existe antes de consultar
    table_name = Producto._meta.db_table
    if table_name not in connection.introspection.table_names():
        return default_context

    try:
        cart = request.session.get('cart', {}) or {}
        # Total de unidades
        cart_count = sum(cart.values()) if cart else 0

        cart_total = Decimal('0.00')
        if cart:
            # Optimizar: obtener precios sólo de los productos presentes
            productos = Producto.objects.filter(id__in=[int(pk) for pk in cart.keys()], is_active=True)
            price_map = {str(product.id): product.price for product in productos}

            for pk, qty in cart.items():
                price = price_map.get(pk)
                if price is None:
                    continue
                cart_total += price * qty

        # Obtener productos organizados por categoría para el menú de catálogo
        productos_activos = Producto.objects.filter(is_active=True).order_by('name')
        productos_por_categoria = defaultdict(list)
        
        for producto in productos_activos:
            # Determinar la categoría para el filtro
            if 'flan' in producto.name.lower():
                categoria = 'flanes'
            elif producto.category == 'galleta':
                categoria = 'galletas'
            elif producto.category == 'pudin':
                categoria = 'pudines'
            else:
                categoria = 'postres'
            
            productos_por_categoria[categoria].append(producto)
        
        # Productos especiales para eventos/cumpleaños
        productos_especiales = Producto.objects.filter(is_active=True, is_special=True).order_by('name')
        
        return {
            'cart_count': cart_count,
            'cart_total': cart_total,
            'productos_por_categoria': dict(productos_por_categoria),
            'postres_especiales': list(productos_especiales)
        }
    except (ProgrammingError, Exception):
        return default_context

def branding(request) -> Dict[str, object]:
    return {
        'project_name': getattr(settings, 'PROJECT_NAME', 'Sweet House'),
        'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@sweethouse.local'),
    }
