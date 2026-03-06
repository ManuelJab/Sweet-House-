from django.db import models

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