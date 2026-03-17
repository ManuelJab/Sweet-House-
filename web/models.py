from django.db import models
from django.conf import settings


class AdminRequest(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	reason = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=(
		('pending', 'Pending'),
		('approved', 'Approved'),
		('rejected', 'Rejected'),
	), default='pending')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"AdminRequest #{self.pk} - {self.user.username} - {self.status}"


# Create your models here.
class SolicitudPedido(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=40, blank=True)
	address = models.TextField(blank=True)
	# keep a nullable FK to Producto (string reference to avoid circular import issues at import time)
	product = models.ForeignKey('tienda.Producto', null=True, blank=True, on_delete=models.SET_NULL)
	product_name = models.CharField(max_length=200, blank=True)
	quantity = models.PositiveIntegerField(default=1)
	notes = models.TextField(blank=True)
	# Personalización del pedido
	size = models.CharField(max_length=20, blank=True)  # pequeño/mediano/grande
	event_message = models.CharField(max_length=200, blank=True)
	event_date = models.DateField(null=True, blank=True)
	occasion = models.CharField(max_length=30, blank=True)  # cumpleaños/aniversario/grado/otro
	# Estado simulado del pedido
	status = models.CharField(max_length=20, default='recibido', choices=(
		('recibido', 'Pedido recibido'),
		('preparacion', 'En preparación'),
		('envio', 'En camino'),
		('entregado', 'Entregado'),
	))
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		pn = self.product_name or (self.product.name if self.product else 'Sin producto')
		return f"Solicitud #{self.pk} - {self.name} - {pn}"


class CustomerFeedback(models.Model):
	name = models.CharField(max_length=120, blank=True)
	email = models.EmailField(blank=True)
	comment = models.TextField()
	# Calificación de atención al cliente 1-5
	rating = models.PositiveSmallIntegerField(default=5)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Feedback #{self.pk} - {self.rating}★"
