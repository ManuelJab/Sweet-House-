"""
Comando para cargar productos con imágenes en la base de datos.
Uso: python manage.py load_products
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from pathlib import Path
from tienda.models import Producto


class Command(BaseCommand):
    help = 'Carga productos con imágenes en la base de datos'

    PRODUCTOS_DATA = [
        {
            'name': 'Cheesecake',
            'description': 'Delicioso cheesecake clásico con base de galleta y topping de frutos rojos.',
            'price': 25000.00,
            'category': 'postre',
            'image_file': 'static/img/cheesecake.jpeg'
        },
        {
            'name': 'Flan Casero',
            'description': 'Flan tradicional con caramelo derretido. Suave, cremoso y delicioso.',
            'price': 12000.00,
            'category': 'postre',
            'image_file': 'static/img/Flan.jpg'
        },
        {
            'name': 'Lava de Chocolate',
            'description': 'Brownie con núcleo de chocolate derretido. Irresistible y tentador.',
            'price': 18000.00,
            'category': 'postre',
            'image_file': 'static/img/lava_chocolate.jpg'
        },
        {
            'name': 'Mousse de Maracuyá',
            'description': 'Mousse ligero y refrescante de maracuyá con toque de vainilla.',
            'price': 16000.00,
            'category': 'postre',
            'image_file': 'static/img/mousse_maracuya.jpg'
        },
        {
            'name': 'Panna Cotta Italiana',
            'description': 'Postre italiano cremoso con toque de vainilla y frutos del bosque.',
            'price': 20000.00,
            'category': 'postre',
            'image_file': 'static/img/panna_Italiana.jpg'
        },
        {
            'name': 'Postre de Chocolate',
            'description': 'Combinación exquisita de chocolate derretido con galleta y frutos secos.',
            'price': 17000.00,
            'category': 'postre',
            'image_file': 'static/img/postre_chocolate.jpeg'
        },
        {
            'name': 'Galletas Integrales',
            'description': 'Galletas crujientes de avena y miel. Saludables y deliciosas.',
            'price': 8000.00,
            'category': 'galleta',
            'image_file': 'static/img/postre_galleta.jpg'
        },
        {
            'name': 'Tartas de Frutas',
            'description': 'Tartas decoradas con frutas frescas y crema pastelera artesanal.',
            'price': 35000.00,
            'category': 'postre',
            'image_file': 'static/img/tartas_frutas.jpg'
        },
        {
            'name': 'Red Velvet',
            'description': 'Clásico pastel rojo aterciopelado con cobertura de queso crema.',
            'price': 28000.00,
            'category': 'postre',
            'image_file': 'static/img/tortared velvet.jpg'
        },
        {
            'name': 'Tres Leches',
            'description': 'Bizcocho bañado en tres tipos de leche. Húmedo, esponjoso y adictivo.',
            'price': 22000.00,
            'category': 'postre',
            'image_file': 'static/img/tres leches.jpg'
        },
        {
            'name': 'Trufas de Chocolate',
            'description': 'Trufas artesanales de chocolate puro recubiertas de cacao. Pura decadencia.',
            'price': 15000.00,
            'category': 'otro',
            'image_file': 'static/img/trufas.jpg'
        },
    ]

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        error_count = 0

        for data in self.PRODUCTOS_DATA:
            try:
                image_path = Path(data['image_file'])

                # Verificar si el producto ya existe
                producto, created = Producto.objects.get_or_create(
                    name=data['name'],
                    defaults={
                        'description': data['description'],
                        'price': data['price'],
                        'category': data['category'],
                        'is_active': True,
                    }
                )

                # Asignar imagen si existe el archivo
                if image_path.exists() and not producto.image:
                    with open(image_path, 'rb') as f:
                        producto.image.save(
                            image_path.name,
                            ContentFile(f.read()),
                            save=True
                        )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Creado: {data["name"]}'))
                    created_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'ℹ️  Existe: {data["name"]}'))
                    updated_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error en {data["name"]}: {str(e)}'))
                error_count += 1

        # Resumen
        self.stdout.write(self.style.SUCCESS('\n📊 Resumen:'))
        self.stdout.write(f'   Creados: {created_count}')
        self.stdout.write(f'   Existentes: {updated_count}')
        self.stdout.write(f'   Errores: {error_count}')
