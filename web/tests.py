from django.test import TestCase, Client
from django.urls import reverse
from web.models import CustomerFeedback, AdminRequest, SolicitudPedido
from tienda.models import Producto
from django.contrib.auth.models import User

class WebViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin = User.objects.create_superuser(username='admin', email='a@a.com', password='password123')
        
        self.producto = Producto.objects.create(
            name='Alfajores',
            category='galleta',
            description='Deliciosos alfajores',
            price=15000.00,
            is_active=True
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_contacto_view(self):
        response = self.client.get(reverse('contacto'))
        self.assertEqual(response.status_code, 200)

    def test_feedback_submission(self):
        response = self.client.post(reverse('feedback'), {
            'name': 'Juan',
            'email': 'juan@example.com',
            'comment': 'Excelente servicio',
            'rating': 5
        })
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertTrue(CustomerFeedback.objects.filter(email='juan@example.com').exists())

    def test_admin_request(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('request_admin'), {
            'reason': 'Quiero ser administrador para editar productos'
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        self.assertTrue(AdminRequest.objects.filter(user=self.user, status='pending').exists())

    def test_solicitud_pedido(self):
        response = self.client.post(reverse('solicitud_pedido'), {
            'name': 'Maria',
            'email': 'maria@example.com',
            'address': 'Calle Falsa 123',
            'product': str(self.producto.id),
            'quantity': 2,
            'event_date': '2026-12-01',
            'occasion': 'cumpleaños'
        })
        self.assertEqual(response.status_code, 302) # Redirects to form view on success
        self.assertTrue(SolicitudPedido.objects.filter(email='maria@example.com', quantity=2).exists())
