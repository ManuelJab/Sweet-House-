from decimal import Decimal
from typing import Dict
from collections import defaultdict

from django.db import connection
from django.db.utils import ProgrammingError

from .models import Producto
from django.conf import settings


def cart_summary(request) -> Dict[str, object]:

    # 🚫 NO ejecutar en admin
    if request.path.startswith('/admin'):
        return {}

    default_context = {
        'cart_count': 0,
        'cart_total': Decimal('0.00'),
        'productos_por_categoria': {},
        'postres_especiales': []
    }

    try:
        table_name = Producto._meta.db_table
        if table_name not in connection.introspection.table_names():
            return default_context

        cart = request.session.get('cart', {}) or {}
        cart_count = sum(cart.values()) if cart else 0

        cart_total = Decimal('0.00')
        if cart:
            productos = Producto.objects.filter(
                id__in=[int(pk) for pk in cart.keys()],
                is_active=True
            )
            price_map = {str(p.id): p.price for p in productos}

            for pk, qty in cart.items():
                price = price_map.get(pk)
                if price:
                    cart_total += price * qty

        productos_activos = Producto.objects.filter(is_active=True).order_by('name')
        productos_por_categoria = defaultdict(list)

        for producto in productos_activos:
            if 'flan' in producto.name.lower():
                categoria = 'flanes'
            elif producto.category == 'galleta':
                categoria = 'galletas'
            elif producto.category == 'pudin':
                categoria = 'pudines'
            else:
                categoria = 'postres'

            productos_por_categoria[categoria].append(producto)

        productos_especiales = Producto.objects.filter(
            is_active=True,
            is_special=True
        ).order_by('name')

        return {
            'cart_count': cart_count,
            'cart_total': cart_total,
            'productos_por_categoria': dict(productos_por_categoria),
            'postres_especiales': list(productos_especiales)
        }

    except (ProgrammingError, Exception):
        return default_context