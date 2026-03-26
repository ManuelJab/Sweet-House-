from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.


class Producto(models.Model):
	name = models.CharField(max_length=120)
	# Marcar productos especiales para eventos/celebraciones
	is_special = models.BooleanField(default=False)
	CATEGORY_CHOICES = [
		('postre', 'Postre'),
		('torta_fria', 'Torta Fría'),
		('pudin', 'Pudín'),
		('otro', 'Otro'),
	]
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='postre')
	description = models.TextField(blank=True)
	ingredients = models.TextField(blank=True, verbose_name='Ingredientes')
	price = models.DecimalField(max_digits=10, decimal_places=2)
	image = models.ImageField(upload_to='productos/', blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.name


class PasswordResetCode(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	email = models.EmailField()
	code_hash = models.CharField(max_length=128)
	attempts = models.PositiveSmallIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	last_sent_at = models.DateTimeField(default=timezone.now)
	expires_at = models.DateTimeField()
	verified_at = models.DateTimeField(null=True, blank=True)
	used_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['email', 'created_at']),
			models.Index(fields=['user', 'created_at']),
			models.Index(fields=['expires_at']),
		]

	def is_expired(self) -> bool:
		return timezone.now() >= self.expires_at

	def can_attempt(self) -> bool:
		return self.attempts < 5 and not self.is_expired() and self.used_at is None
