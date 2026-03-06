import os
import sys
sys.path.append('Stiman-Dessert-main')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stimandessert.settings')
import django
django.setup()
from tienda.models import Producto
from django.core.files import File

MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'productos')
examples = [
    ('Flan', 'Delicioso flan casero', 'productos/Flan.jpg', 'postre', '12900.00'),
    ('Lava Choco', 'Brownie con interior derretido', 'productos/lava_chocolate.jpg', 'postre', '1900.00'),
    ('Torta Especial', 'Torta red velvet especial', 'productos/tortared_velvet.jpg', 'postre', '12900.00'),
    ('Tres Leches', 'Clásico tres leches', 'productos/tres_leches.jpg', 'postre', '18000.00'),
    ('Cheesecake', 'Cheesecake cremoso', 'productos/cheesecake.jpeg', 'postre', '12900.00'),
]

created = []
for name, desc, img_path, category, price in examples:
    prod, created_flag = Producto.objects.get_or_create(name=name, defaults={
        'description': desc,
        'price': price,
        'category': category,
        'is_active': True,
    })
    # set image if file exists and not already set
    full_img = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', img_path)
    if img_path and os.path.exists(full_img):
        if not prod.image:
            # update the underlying DB field directly with the relative path
            Producto.objects.filter(pk=prod.pk).update(image=img_path)
            prod.refresh_from_db()
    created.append((prod.id, prod.name, bool(prod.image)))

print('Seed complete. Products:')
for p in created:
    print(p)
