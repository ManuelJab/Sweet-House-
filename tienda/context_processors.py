from decimal import Decimal
from django.conf import settings
from django.db import connection
from django.db.utils import ProgrammingError
from .models import Producto


def cart_summary(request):

    # No ejecutar en admin
    if request.path.startswith('/admin'):
        return {}

    try:
        cart = request.session.get('cart', {}) or {}
        cart_count = int(sum(cart.values())) if cart else 0

        return {
            'cart_count': cart_count,
            'cart_total': float(0),
            'productos_por_categoria': {},
            'postres_especiales': []
        }

    except Exception:
        return {
            'cart_count': 0,
            'cart_total': 0,
            'productos_por_categoria': {},
            'postres_especiales': []
        }


def branding(request):
    return {
        'project_name': 'Sweet House',
        'support_email': 'no-reply@sweethouse.local',
    }