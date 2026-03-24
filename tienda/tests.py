from django.test import TestCase, Client
from django.urls import reverse
from tienda.models import Producto
from django.contrib.auth.models import User

class ProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            name='Torta de Chocolate',
            is_special=False,
            category='postre',
            description='Deliciosa torta de chocolate.',
            price=25000.00,
            is_active=True
        )

    def test_producto_creado_correctamente(self):
        """Valida que el producto se haya creado y devuelva el nombre correcto."""
        producto = Producto.objects.get(id=self.producto.id)
        self.assertEqual(producto.name, 'Torta de Chocolate')
        self.assertEqual(str(producto), 'Torta de Chocolate')

    def test_precio_producto(self):
        """Valida se guarde el precio esperado."""
        self.assertEqual(self.producto.price, 25000.00)

class TiendaViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin = User.objects.create_superuser(username='admin', email='a@a.com', password='password123')
        
        self.producto = Producto.objects.create(
            name='Cheesecake de Fresa',
            category='torta_fria',
            price=30000.00,
            is_active=True
        )

    def test_catalogo_publico_view_status_code(self):
        """Valida que la vista del catálogo responda con un HTTP 200 OK y contenta el producto."""
        response = self.client.get(reverse('catalogo_publico'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cheesecake de Fresa')

    def test_add_to_cart(self):
        """Valida que se pueda añadir un producto al carrito en sesión."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('carrito_agregar', args=[self.producto.id]), {'qty': 2})
        self.assertEqual(response.status_code, 302) # Redirects to cart detail
        
        # To access the updated session after a request in Django test client
        session = self.client.session
        self.assertEqual(session.get('cart', {}).get(str(self.producto.id)), 2)

    def test_toggle_favorites(self):
        """Valida que se pueda añadir/quitar de favoritos."""
        self.client.login(username='testuser', password='password123')
        # Use HTTP_REFERER so it redirects back correctly
        response = self.client.get(reverse('favoritos_toggle', args=[self.producto.id]), HTTP_REFERER=reverse('catalogo_publico'))
        self.assertEqual(response.status_code, 302)
        
        session = self.client.session
        self.assertIn(str(self.producto.id), session.get('favorites', []))

    def test_checkout_view_with_empty_cart(self):
        """Valida que el checkout redirija si el carrito está vacío."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302) # Redirects to cart detail
        
    def test_checkout_view_with_items(self):
        """Valida que el checkout muestre los items a pagar."""
        self.client.login(username='testuser', password='password123')
        # Add item to cart first
        session = self.client.session
        session['cart'] = {str(self.producto.id): 1}
        session.save()
        
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cheesecake de Fresa')
