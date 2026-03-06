from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.db import models
from .forms import EmailUserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Producto



from django.db.models import Sum, Count

def inicio(request):
	return render(request, 'tienda/inicio.html')


def home(request):
	"""Vista para la página de inicio que muestra los más vendidos y recomendados."""
	# Importar SolicitudPedido localmente para evitar ciclos si es necesario, 
	# aunque idealmente debería estar arriba si no hay ciclo.
	from web.models import SolicitudPedido
	
	# 1. Más vendidos: Productos con mayor cantidad total en SolicitudPedidos
	# Filtramos por status para contar solo pedidos reales si se desea, 
	# pero por simplicidad contamos todos.
	# Anotamos cada producto con la suma de 'quantity' de sus pedidos.
	mas_vendidos = Producto.objects.filter(is_active=True).annotate(
		total_sold=Sum('solicitudpedido__quantity')
	).order_by('-total_sold')[:4]
	
	# 2. Recomendados: Productos marcados como is_special o simplemente aleatorios/nuevos
	recomendados = Producto.objects.filter(is_active=True, is_special=True).order_by('-created_at')[:4]
	
	# Si no hay suficientes especiales, rellenar con los más recientes
	if recomendados.count() < 4:
		extras = Producto.objects.filter(is_active=True, is_special=False).order_by('-created_at')[:4 - recomendados.count()]
		recomendados = list(recomendados) + list(extras)
	
	return render(request, 'index.html', {
		'mas_vendidos': mas_vendidos,
		'recomendados': recomendados
	})


class ProductoForm(forms.ModelForm):
	class Meta:
		model = Producto
		fields = ['name', 'description', 'ingredients', 'price', 'image', 'category', 'is_special', 'is_active']
		labels = {
			'name': 'Nombre del producto',
			'description': 'Descripción',
			'ingredients': 'Ingredientes',
			'price': 'Precio',
			'image': 'Imagen',
			'is_special': 'Especial para eventos',
			'is_active': 'Activo',
		}
		help_texts = {
			'name': 'Entre 3 y 120 caracteres. Debe ser único y descriptivo.',
			'description': 'Describe ingredientes, tamaño, porciones o notas especiales.',
			'ingredients': 'Lista de ingredientes del producto separados por coma.',
			'price': 'Usa punto para decimales. Ej: 12900.00',
			'image': 'Formatos JPG o PNG recomendados. Máx. 2MB.',
			'category': 'Selecciona la categoría: postre, galleta o pudín.'
		}
		widgets = {
			'name': forms.TextInput(attrs={
				'placeholder': 'Ej: Tarta de chocolate con fresas',
				'class': 'input',
				'maxlength': '120',
				'autofocus': 'autofocus',
			}),
			'description': forms.Textarea(attrs={
				'placeholder': 'Breve descripción del producto...',
				'rows': 4,
				'class': 'textarea',
				'data-counter': 'true',
				'maxlength': '600',
			}),
			'ingredients': forms.Textarea(attrs={
				'placeholder': 'Ej: Harina, azúcar, huevos, mantequilla, chocolate...',
				'rows': 3,
				'class': 'textarea',
				'maxlength': '500',
			}),
			'price': forms.NumberInput(attrs={
				'placeholder': '0.00',
				'step': '0.01',
				'min': '0',
				'class': 'input',
				'inputmode': 'decimal',
				'data-currency': 'COP',
			}),
			'image': forms.ClearableFileInput(attrs={
				'accept': 'image/*',
				'class': 'file-input',
				'data-dropzone': 'true',
			}),
			'category': forms.Select(attrs={
				'class': 'input'
			}),
			'is_special': forms.CheckboxInput(attrs={
				'class': 'switch-input',
			}),
			'is_active': forms.CheckboxInput(attrs={
				'class': 'switch-input',
			}),
		}

	def clean_name(self):
		name = (self.cleaned_data.get('name') or '').strip()
		if len(name) < 3:
			raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
		return name

	def clean_description(self):
		description = (self.cleaned_data.get('description') or '').strip()
		return description

	def clean_price(self):
		price = self.cleaned_data.get('price')
		if price is None:
			raise forms.ValidationError('Debes indicar un precio.')
		if price <= 0:
			raise forms.ValidationError('El precio debe ser mayor que 0.')
		return price


@staff_member_required
def admin_dashboard(request):
    from django.db.models import Count, Sum, F
    from django.db.models.functions import TruncDate, TruncMonth
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Basic Stats
    productos_total = Producto.objects.count()
    productos_activos = Producto.objects.filter(is_active=True).count()
    productos_recientes = Producto.objects.order_by('-created_at')[:5]
    
    # Load solicitudes
    try:
        from web.models import SolicitudPedido
        solicitudes_total = SolicitudPedido.objects.count()
        solicitudes_recientes = SolicitudPedido.objects.order_by('-created_at')[:5]
        
        # --- Charts Data ---
        
        # 1. Best Sellers (Top 5 Products by Quantity)
        # Group by product_name because product FK might be null if deleted, 
        # but product_name is preserved.
        best_sellers_qs = SolicitudPedido.objects.values('product_name') \
            .annotate(total_qty=Sum('quantity')) \
            .order_by('-total_qty')[:5]
            
        best_sellers_labels = [item['product_name'] or 'Sin nombre' for item in best_sellers_qs]
        best_sellers_data = [item['total_qty'] for item in best_sellers_qs]
        
        # 2. Daily Sales (Last 30 Days) - Count of orders
        last_30_days = timezone.now() - timedelta(days=30)
        daily_sales_qs = SolicitudPedido.objects.filter(created_at__gte=last_30_days) \
            .annotate(date=TruncDate('created_at')) \
            .values('date') \
            .annotate(count=Count('id')) \
            .order_by('date')
            
        daily_sales_labels = [item['date'].strftime('%d/%m') for item in daily_sales_qs]
        daily_sales_data = [item['count'] for item in daily_sales_qs]
        
        # 3. Monthly Income (Estimated) - Last 6 Months
        # Since SolicitudPedido doesn't store price at time of purchase, we fetch current price.
        # This is an estimation.
        # We need to fetch objects to multiply qty * product.price manually 
        # because price is on a related model.
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_orders = SolicitudPedido.objects.filter(created_at__gte=six_months_ago) \
            .select_related('product')
            
        monthly_income_dict = {} # "YYYY-MM" -> total
        
        for order in monthly_orders:
            month_key = order.created_at.strftime('%Y-%m')
            price = order.product.price if order.product else 0 
            # If product is deleted, price is 0 (limitation of current model)
            current_total = monthly_income_dict.get(month_key, 0)
            monthly_income_dict[month_key] = current_total + (price * order.quantity)
            
        # Sort by month
        sorted_months = sorted(monthly_income_dict.keys())
        monthly_income_labels = sorted_months
        monthly_income_data = [monthly_income_dict[m] for m in sorted_months]

        # 4. Customers (Unique Emails)
        unique_customers_count = SolicitudPedido.objects.values('email').distinct().count()
        
    except Exception as e:
        print(f"Error in dashboard stats: {e}")
        solicitudes_total = 0
        solicitudes_recientes = []
        best_sellers_labels = []
        best_sellers_data = []
        daily_sales_labels = []
        daily_sales_data = []
        monthly_income_labels = []
        monthly_income_data = []
        unique_customers_count = 0

    context = {
        'is_admin': True,
        'productos_total': productos_total,
        'productos_activos': productos_activos,
        'productos': productos_recientes,
        'solicitudes_total': solicitudes_total,
        'solicitudes': solicitudes_recientes,
        'unique_customers_count': unique_customers_count,
        # Charts
        'best_sellers_labels': best_sellers_labels,
        'best_sellers_data': best_sellers_data,
        'daily_sales_labels': daily_sales_labels,
        'daily_sales_data': daily_sales_data,
        'monthly_income_labels': monthly_income_labels,
        'monthly_income_data': monthly_income_data,
    }
    return render(request, 'dashboard.html', context)


@staff_member_required
def productos_list(request):
	q = request.GET.get('q', '').strip()
	productos_qs = Producto.objects.all().order_by('-created_at')
	if q:
		productos_qs = productos_qs.filter(name__icontains=q)
	paginator = Paginator(productos_qs, 10)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	return render(request, 'tienda/productos_list.html', {
		'productos': page_obj.object_list,
		'page_obj': page_obj,
		'q': q,
	})


@staff_member_required
def producto_create(request):
	if request.method == 'POST':
		form = ProductoForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('productos_list')
	else:
		form = ProductoForm()
	return render(request, 'tienda/producto_form.html', {'form': form, 'is_create': True})


def producto_public_create(request):
	"""Vista pública para que usuarios agreguen productos (postre/galleta/pudín)."""
	if request.method == 'POST':
		form = ProductoForm(request.POST, request.FILES)
		if form.is_valid():
			producto = form.save(commit=False)
			# Por simplicidad dejamos el producto activo. Si prefieres moderación,
			# puedes poner producto.is_active = False y avisar al admin.
			producto.save()
			from django.contrib import messages
			messages.success(request, 'Producto añadido correctamente.')
			return redirect('catalogo_publico')
	else:
		form = ProductoForm()
	return render(request, 'tienda/producto_form.html', {'form': form, 'is_create': True, 'back_url': reverse('catalogo_publico')})


@staff_member_required
def producto_update(request, pk: int):
	producto = get_object_or_404(Producto, pk=pk)
	# Capturar URL de retorno (prioridad POST, luego GET)
	back_url = request.POST.get('next') or request.GET.get('next')

	if request.method == 'POST':
		form = ProductoForm(request.POST, request.FILES, instance=producto)
		if form.is_valid():
			form.save()
			if back_url and url_has_allowed_host_and_scheme(back_url, allowed_hosts={request.get_host()}):
				return redirect(back_url)
			return redirect('productos_list')
	else:
		form = ProductoForm(instance=producto)
	return render(request, 'tienda/producto_form.html', {'form': form, 'is_create': False, 'back_url': back_url})


@staff_member_required
def producto_delete(request, pk: int):
	producto = get_object_or_404(Producto, pk=pk)
	if request.method == 'POST':
		producto.delete()
		return redirect('productos_list')
	return render(request, 'tienda/producto_confirm_delete.html', {'producto': producto})


# Registro
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse

def signup(request):
	if request.user.is_authenticated:
		return redirect('catalogo_publico')
    
	if request.method == 'POST':
		form = EmailUserCreationForm(request.POST)
		if form.is_valid():
			try:
				user = form.save()
				# Ensure newly registered users are not staff/superuser by default
				user.is_staff = False
				user.is_superuser = False
				user.save()
				first_name = user.first_name if user.first_name else user.username
				messages.success(request, f'¡Registro exitoso! Tu cuenta ha sido creada. Por favor, inicia sesión con tus credenciales.')
				# Mostrar página de confirmación con el username generado
				return render(request, 'registration/signup_success.html', {'username': user.username, 'first_name': first_name})
			except Exception:
				form.add_error(None, 'Error al crear la cuenta. Por favor, intente nuevamente.')
	else:
		form = EmailUserCreationForm()
    
	return render(request, 'registration/signup.html', {'form': form})


class CustomLoginView(LoginView):
	"""Login view that redirects staff to the admin dashboard and normal users to home."""
	def get_success_url(self):
		# If a `next` parameter exists and is safe, allow it — except when it points to /admin/
		next_url = self.request.POST.get(self.redirect_field_name) or self.request.GET.get(self.redirect_field_name)
		if next_url:
			# ensure it's a safe URL for this host
			if url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
				# ignore admin area redirects for security/usability
				if next_url.startswith('/admin'):
					next_url = None
				else:
					return next_url

		user = self.request.user
		if user.is_active and (user.is_staff or user.is_superuser):
			return reverse('dashboard')
		return reverse('home')

	def form_valid(self, form):
		response = super().form_valid(form)
		user = self.request.user
		first_name = user.first_name if user.first_name else user.username
		messages.success(self.request, f'¡Bienvenido {first_name}! Has iniciado sesión correctamente.')
		return response


# Carrito en sesión

def _get_cart(session):
	cart = session.get('cart')
	if cart is None:
		cart = {}
		session['cart'] = cart
	return cart


def cart_detail(request):
	cart = _get_cart(request.session)
	items = []
	total = 0
	for pk_str, qty in cart.items():
		try:
			product = Producto.objects.get(pk=int(pk_str), is_active=True)
		except Producto.DoesNotExist:
			continue
		subtotal = product.price * qty
		total += subtotal
		items.append({
			'product': product,
			'qty': qty,
			'subtotal': subtotal,
		})
	return render(request, 'tienda/carrito_detalle.html', {'items': items, 'total': total})


@require_POST
def cart_add(request, pk: int):
	product = get_object_or_404(Producto, pk=pk, is_active=True)
	qty = int(request.POST.get('qty', '1'))
	qty = 1 if qty < 1 else qty
	cart = _get_cart(request.session)
	pk_str = str(product.pk)
	cart[pk_str] = cart.get(pk_str, 0) + qty
	request.session.modified = True
	return redirect('carrito_detalle')


@require_POST
def cart_update(request, pk: int):
	product = get_object_or_404(Producto, pk=pk)
	qty = int(request.POST.get('qty', '1'))
	cart = _get_cart(request.session)
	pk_str = str(product.pk)
	if qty <= 0:
		cart.pop(pk_str, None)
	else:
		cart[pk_str] = qty
	request.session.modified = True
	return redirect('carrito_detalle')


@require_POST
def cart_remove(request, pk: int):
	product = get_object_or_404(Producto, pk=pk)
	cart = _get_cart(request.session)
	cart.pop(str(product.pk), None)
	request.session.modified = True
	return redirect('carrito_detalle')


@require_POST
def cart_clear(request):
	request.session['cart'] = {}
	request.session.modified = True
	return redirect('carrito_detalle')

# Favoritos (por sesión)
def _get_favorites(session):
	favs = session.get('favorites')
	if favs is None:
		favs = set()
		session['favorites'] = list(favs)
	return set(session.get('favorites', []))

def favoritos_toggle(request, pk: int):
	product = get_object_or_404(Producto, pk=pk, is_active=True)
	favs = _get_favorites(request.session)
	pk_str = str(product.pk)
	if pk_str in favs:
		favs.remove(pk_str)
	else:
		favs.add(pk_str)
	request.session['favorites'] = list(favs)
	request.session.modified = True
	return redirect(request.META.get('HTTP_REFERER', 'catalogo_publico'))

def favoritos_list(request):
	favs = _get_favorites(request.session)
	ids = [int(x) for x in favs]
	productos = Producto.objects.filter(id__in=ids, is_active=True).order_by('name')
	return render(request, 'tienda/favoritos_list.html', {'productos': productos})

# Catálogo público (desde DB)

def catalogo_publico(request):
	productos = Producto.objects.filter(is_active=True).order_by('name')
	return render(request, 'tienda/catalogo_publico.html', {'productos': productos})


def catalogo_estilizado(request):
	productos = Producto.objects.filter(is_active=True).order_by('name')
	return render(request, 'catalogo.html', {'productos': productos})


# Checkout con instrucciones de pago Nequi

def checkout(request):
	cart = _get_cart(request.session)
	if not cart:
		return redirect('carrito_detalle')
	# Calcular total
	total = 0
	items = []
	for pk_str, qty in cart.items():
		try:
			product = Producto.objects.get(pk=int(pk_str))
		except Producto.DoesNotExist:
			continue
		subtotal = product.price * qty
		total += subtotal
		items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
	if request.method == 'POST':
		# Aquí podrías registrar el pedido y limpiar el carrito
		request.session['cart'] = {}
		request.session.modified = True
		return render(request, 'tienda/checkout_exito.html', {'total': total})
	nequi_number = '3015096797'  # Cambia por tu número Nequi
	return render(request, 'tienda/checkout.html', {'items': items, 'total': total, 'nequi_number': nequi_number})


# Gestión de Solicitudes de Pedido

@staff_member_required
def solicitudes_list(request):
	"""Listar y gestionar todas las solicitudes de pedido."""
	from web.models import SolicitudPedido
	
	# Filtros
	q = request.GET.get('q', '').strip()
	product_filter = request.GET.get('product', '').strip()
	date_from = request.GET.get('date_from', '').strip()
	date_to = request.GET.get('date_to', '').strip()
	
	solicitudes_qs = SolicitudPedido.objects.all().order_by('-created_at')
	
	# Búsqueda por nombre, email, teléfono
	if q:
		solicitudes_qs = solicitudes_qs.filter(
			models.Q(name__icontains=q) |
			models.Q(email__icontains=q) |
			models.Q(phone__icontains=q)
		)
	
	# Filtro por producto
	if product_filter:
		solicitudes_qs = solicitudes_qs.filter(product_name__icontains=product_filter)
	
	# Filtro por rango de fechas
	if date_from:
		try:
			from datetime import datetime
			df = datetime.strptime(date_from, '%Y-%m-%d').date()
			solicitudes_qs = solicitudes_qs.filter(created_at__date__gte=df)
		except:
			pass
	
	if date_to:
		try:
			from datetime import datetime
			dt = datetime.strptime(date_to, '%Y-%m-%d').date()
			solicitudes_qs = solicitudes_qs.filter(created_at__date__lte=dt)
		except:
			pass
	
	# Paginación
	paginator = Paginator(solicitudes_qs, 15)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	# Lista de productos únicos para dropdown
	productos_unicos = set(SolicitudPedido.objects.values_list('product_name', flat=True).distinct())
	
	context = {
		'solicitudes': page_obj.object_list,
		'page_obj': page_obj,
		'q': q,
		'product_filter': product_filter,
		'date_from': date_from,
		'date_to': date_to,
		'productos_unicos': sorted(productos_unicos),
		'total_solicitudes': SolicitudPedido.objects.count(),
	}
	
	return render(request, 'tienda/solicitudes_list.html', context)


@staff_member_required
def solicitud_detail(request, pk: int):
	"""Ver detalles de una solicitud específica."""
	from web.models import SolicitudPedido
	solicitud = get_object_or_404(SolicitudPedido, pk=pk)
	return render(request, 'tienda/solicitud_detail.html', {'solicitud': solicitud})

@staff_member_required
def solicitud_avanzar_estado(request, pk: int):
	from web.models import SolicitudPedido
	s = get_object_or_404(SolicitudPedido, pk=pk)
	order = ['recibido', 'preparacion', 'envio', 'entregado']
	try:
		idx = order.index(s.status)
		if idx < len(order) - 1:
			s.status = order[idx + 1]
			s.save()
			messages.success(request, f"Estado avanzado a: {dict((k, v) for k, v in s._meta.get_field('status').choices)[s.status]}")
		else:
			messages.info(request, "La solicitud ya está en estado final: entregado.")
	except Exception:
		messages.error(request, "No se pudo avanzar el estado.")
	return redirect('solicitud_detail', pk=pk)


@staff_member_required
def clientes_list(request):
    """Listar clientes únicos basados en solicitudes de pedido."""
    from web.models import SolicitudPedido
    from django.db.models import Count, Max
    
    # Agrupar por email para obtener clientes únicos
    # Anotamos con la última fecha de pedido y total de pedidos
    clientes = SolicitudPedido.objects.values('email') \
        .annotate(
            total_orders=Count('id'),
            last_order=Max('created_at'),
            name=Max('name'), # Simple approach to get a name
            phone=Max('phone')
        ) \
        .order_by('-last_order')
        
    return render(request, 'tienda/clientes_list.html', {'clientes': clientes})
