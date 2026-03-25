from django.contrib import admin
from django.contrib import messages
from .models import SolicitudPedido, AdminRequest, CustomerFeedback


@admin.register(SolicitudPedido)
class SolicitudPedidoAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'product_name', 'quantity', 'email', 'created_at')
	list_filter = ('created_at',)
	search_fields = ('name', 'email', 'product_name')
	ordering = ('-created_at',)

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'email', 'rating', 'created_at')
	list_filter = ('rating', 'created_at')
	search_fields = ('name', 'email', 'comment')
	ordering = ('-created_at',)


@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('user__username', 'user__email')
	actions = ['approve_requests', 'reject_requests']

	def approve_requests(self, request, queryset):
		updated = 0
		for req in queryset.filter(status='pending'):
			user = req.user
			user.is_staff = True
			user.save()
			req.status = 'approved'
			req.save()
			updated += 1
		self.message_user(request, f"Aprobadas {updated} solicitudes y asignado is_staff.", level=messages.SUCCESS)
	approve_requests.short_description = 'Approve selected admin requests (make user staff)'

	def reject_requests(self, request, queryset):
		updated = queryset.filter(status='pending').update(status='rejected')
		self.message_user(request, f"Rechazadas {updated} solicitudes.", level=messages.INFO)
	reject_requests.short_description = 'Reject selected admin requests'
