from django.urls import path
from . import views

urlpatterns = [
	path('', views.inicio, name='tienda_inicio'),
	path('productos/', views.productos_list, name='productos_list'),
	path('productos/reporte/', views.productos_reporte, name='productos_reporte'),
	path('productos/nuevo/', views.producto_create, name='producto_create'),
	path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
	path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
	path('signup/', views.signup, name='signup'),
	# público
	path('catalogo/', views.catalogo_publico, name='catalogo_publico'),
    path('catalogo/agregar/', views.producto_public_create, name='producto_public_create'),
	# carrito
	path('carrito/', views.cart_detail, name='carrito_detalle'),
	path('carrito/agregar/<int:pk>/', views.cart_add, name='carrito_agregar'),
	path('carrito/actualizar/<int:pk>/', views.cart_update, name='carrito_actualizar'),
	path('carrito/eliminar/<int:pk>/', views.cart_remove, name='carrito_eliminar'),
	path('carrito/vaciar/', views.cart_clear, name='carrito_vaciar'),
	# checkout nequi
	path('checkout/', views.checkout, name='checkout'),
	# solicitudes de pedido
	path('mis-pedidos/', views.pedidos_usuario, name='pedidos_usuario'),
	path('solicitudes/', views.solicitudes_list, name='solicitudes_list'),
    path('clientes/', views.clientes_list, name='clientes_list'),
	path('solicitudes/<int:pk>/', views.solicitud_detail, name='solicitud_detail'),
	path('solicitudes/<int:pk>/avanzar/', views.solicitud_avanzar_estado, name='solicitud_avanzar_estado'),
    path('solicitudes/<int:pk>/enviar-email/', views.solicitud_enviar_email, name='solicitud_enviar_email'),
    # dashboard metrics (json)
    path('dashboard/metrics/', views.dashboard_metrics, name='dashboard_metrics'),
	# favoritos
	path('favoritos/', views.favoritos_list, name='favoritos_list'),
	path('favoritos/toggle/<int:pk>/', views.favoritos_toggle, name='favoritos_toggle'),
]
