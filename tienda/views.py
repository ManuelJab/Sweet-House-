from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.db import models
from django.conf import settings
from .forms import EmailUserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Producto
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


from django.contrib.auth.decorators import login_required


from django.db.models import Sum, Count
from decimal import Decimal, ROUND_HALF_UP
import os
from dotenv import load_dotenv
from django.http import JsonResponse

def inicio(request):
	return render(request, 'tienda/inicio.html')


def home(request):
	"""Vista para la página de inicio que muestra los más vendidos y recomendados."""
	# Importar SolicitudPedido localmente para evitar ciclos
	from web.models import SolicitudPedido
	from django.db import connection

	# Verificar si las tablas existen para evitar Error 500 antes de migrate
	tables = connection.introspection.table_names()
	if Producto._meta.db_table not in tables:
		return render(request, 'index.html', {'mas_vendidos': [], 'recomendados': []})

	try:
		# 1. Más vendidos
		mas_vendidos = Producto.objects.filter(is_active=True).annotate(
			total_sold=Sum('solicitudpedido__quantity')
		).order_by('-total_sold')[:4]
		
		# 2. Recomendados
		recomendados = Producto.objects.filter(is_active=True, is_special=True).order_by('-created_at')[:4]
		
		# Si no hay suficientes especiales, rellenar con los más recientes
		if recomendados.count() < 4:
			extras = Producto.objects.filter(is_active=True, is_special=False).order_by('-created_at')[:4 - recomendados.count()]
			recomendados = list(recomendados) + list(extras)
		
		return render(request, 'index.html', {
			'mas_vendidos': mas_vendidos,
			'recomendados': recomendados,
		})
	except Exception:
		# En caso de cualquier otro error de DB, mostrar página básica
		return render(request, 'index.html', {'mas_vendidos': [], 'recomendados': []})


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
    productos_inactivos = Producto.objects.filter(is_active=False).count()
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

        # 4. This Month KPIs
        now_dt = timezone.now()
        start_of_month = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_qs = SolicitudPedido.objects.filter(created_at__gte=start_of_month).select_related('product')
        pedidos_nuevos = month_qs.count()
        monthly_sales_total = 0
        for o in month_qs:
            monthly_sales_total += (o.product.price if o.product else 0) * o.quantity
        # Unique customers this month
        unique_customers_count = month_qs.values('email').distinct().count()
        
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
        pedidos_nuevos = 0
        monthly_sales_total = 0

    context = {
        'is_admin': True,
        'now': timezone.now(),
        'productos_total': productos_total,
        'productos_activos': productos_activos,
        'productos_inactivos': productos_inactivos,
        'productos': productos_recientes,
        'solicitudes_total': solicitudes_total,
        'pedidos_nuevos': pedidos_nuevos,
        'solicitudes': solicitudes_recientes,
        'unique_customers_count': unique_customers_count,
        'monthly_sales_total': monthly_sales_total,
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
def dashboard_metrics(request):
    """Devuelve métricas del dashboard en JSON para refresco automático."""
    from django.utils import timezone
    from django.db.models.functions import TruncDate
    from web.models import SolicitudPedido
    now_dt = timezone.now()
    productos_activos = Producto.objects.filter(is_active=True).count()
    productos_inactivos = Producto.objects.filter(is_active=False).count()
    # Ventas diarias (últimos 30 días)
    last_30 = now_dt - timezone.timedelta(days=30)
    daily = (SolicitudPedido.objects.filter(created_at__gte=last_30)
             .annotate(date=TruncDate('created_at'))
             .values('date')
             .annotate(count=Count('id'))
             .order_by('date'))
    daily_labels = [item['date'].strftime('%d/%m') for item in daily]
    daily_data = [item['count'] for item in daily]
    # Más vendidos (top 5)
    best = (SolicitudPedido.objects.values('product_name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:5])
    best_labels = [b['product_name'] or 'Sin nombre' for b in best]
    best_data = [b['total_qty'] for b in best]
    # Ingresos mensuales (últimos 6 meses, estimado)
    six_months_ago = now_dt - timezone.timedelta(days=180)
    monthly_orders = SolicitudPedido.objects.filter(created_at__gte=six_months_ago).select_related('product')
    monthly_map = {}
    month_sales_total = 0
    start_month = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for o in monthly_orders:
        key = o.created_at.strftime('%Y-%m')
        amt = (o.product.price if o.product else 0) * o.quantity
        monthly_map[key] = monthly_map.get(key, 0) + amt
        if o.created_at >= start_month:
            month_sales_total += amt
    monthly_labels = sorted(monthly_map.keys())
    monthly_data = [monthly_map[m] for m in monthly_labels]
    pedidos_nuevos = SolicitudPedido.objects.filter(created_at__gte=start_month).count()
    unique_customers = (SolicitudPedido.objects.filter(created_at__gte=start_month)
                        .values('email').distinct().count())
    return JsonResponse({
        'productos_activos': productos_activos,
        'productos_inactivos': productos_inactivos,
        'daily_sales_labels': daily_labels,
        'daily_sales_data': daily_data,
        'best_sellers_labels': best_labels,
        'best_sellers_data': best_data,
        'monthly_income_labels': monthly_labels,
        'monthly_income_data': monthly_data,
        'monthly_sales_total': float(month_sales_total),
        'pedidos_nuevos': pedidos_nuevos,
        'unique_customers_count': unique_customers,
        'generated_at': now_dt.isoformat(),
    })

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
def productos_reporte(request):
	"""Vista imprimible para exportar/guardar en PDF la lista completa de productos."""
	productos = Producto.objects.all().order_by('name')
	return render(request, 'tienda/productos_reporte.html', {
		'productos': productos,
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


from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST as require_post_method

@require_post_method
def ajax_login(request):
	"""AJAX login endpoint for the modal. Returns JSON."""
	username = request.POST.get('username', '').strip()
	password = request.POST.get('password', '')

	if not username or not password:
		return JsonResponse({'success': False, 'error': 'Por favor, completa todos los campos.'})

	user = authenticate(request, username=username, password=password)
	if user is not None:
		if user.is_active:
			auth_login(request, user)
			first_name = user.first_name if user.first_name else user.username
			messages.success(request, f'¡Bienvenido {first_name}! Has iniciado sesión correctamente.')
			# Determine redirect URL
			if user.is_staff or user.is_superuser:
				redirect_url = reverse('dashboard')
			else:
				redirect_url = reverse('home')
			return JsonResponse({'success': True, 'redirect_url': redirect_url})
		else:
			return JsonResponse({'success': False, 'error': 'Tu cuenta está desactivada.'})
	else:
		return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos.'})


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
@login_required
def cart_add(request, pk: int):
	if request.user.is_staff or request.user.is_superuser:
		messages.info(request, 'Los administradores no pueden comprar. Usa el dashboard para gestionar productos.')
		return redirect('catalogo_publico')
	product = get_object_or_404(Producto, pk=pk, is_active=True)
	qty = int(request.POST.get('qty', '1'))
	qty = 1 if qty < 1 else qty
	cart = _get_cart(request.session)
	pk_str = str(product.pk)
	cart[pk_str] = cart.get(pk_str, 0) + qty
	request.session.modified = True
	return redirect('carrito_detalle')


@require_POST
@login_required
def cart_update(request, pk: int):
	if request.user.is_staff or request.user.is_superuser:
		messages.info(request, 'Los administradores no pueden modificar el carrito.')
		return redirect('carrito_detalle')
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
@login_required
def cart_remove(request, pk: int):
	if request.user.is_staff or request.user.is_superuser:
		messages.info(request, 'Los administradores no pueden modificar el carrito.')
		return redirect('carrito_detalle')
	product = get_object_or_404(Producto, pk=pk)
	cart = _get_cart(request.session)
	cart.pop(str(product.pk), None)
	request.session.modified = True
	return redirect('carrito_detalle')


@require_POST
@login_required
def cart_clear(request):
	if request.user.is_staff or request.user.is_superuser:
		messages.info(request, 'Los administradores no pueden modificar el carrito.')
		return redirect('carrito_detalle')
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
	if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
		messages.info(request, 'Los administradores no pueden gestionar favoritos.')
		return redirect(request.META.get('HTTP_REFERER', 'catalogo_publico'))
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
	postres_especiales = Producto.objects.filter(is_active=True, is_special=True).order_by('name')
	favorites_ids = _get_favorites(request.session)
	return render(request, 'tienda/catalogo_publico.html', {
		'productos': productos,
		'postres_especiales': postres_especiales,
		'favorites_ids': favorites_ids
	})


def catalogo_estilizado(request):
	productos = Producto.objects.filter(is_active=True).order_by('name')
	return render(request, 'catalogo.html', {'productos': productos})


# Checkout con instrucciones de pago Nequi

@login_required
def checkout(request):
	if request.user.is_staff or request.user.is_superuser:
		messages.info(request, 'Los administradores no pueden realizar pagos.')
		return redirect('dashboard')
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
		from web.models import SolicitudPedido
		# Creamos una solicitud por cada item en el carrito
		created_ids = []
		for item in items:
			o = SolicitudPedido.objects.create(
				name=request.user.get_full_name() or request.user.username,
				email=request.user.email,
				product=item['product'],
				product_name=item['product'].name,
				quantity=item['qty'],
				notes=f"Pago realizado via Checkout (Total: {total})",
				status='recibido'
			)
			created_ids.append(o.pk)
		request.session['cart'] = {}
		request.session.modified = True
		try:
			host = os.environ.get('EMAIL_HOST') or getattr(settings, 'EMAIL_HOST', '')
			user = os.environ.get('EMAIL_HOST_USER') or getattr(settings, 'EMAIL_HOST_USER', '')
			password = os.environ.get('EMAIL_HOST_PASSWORD') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
			try:
				port = int(os.environ.get('EMAIL_PORT') or getattr(settings, 'EMAIL_PORT', 587))
			except Exception:
				port = 587
			use_tls = (os.environ.get('EMAIL_USE_TLS') or str(getattr(settings, 'EMAIL_USE_TLS', True))).lower() in ('true', '1', 'yes')
			use_ssl = (os.environ.get('EMAIL_USE_SSL') or str(getattr(settings, 'EMAIL_USE_SSL', False))).lower() in ('true', '1', 'yes')
			smtp_ready = bool(host and user and password)
			if smtp_ready:
				conn = get_connection('django.core.mail.backends.smtp.EmailBackend',
					host=host, port=port, username=user, password=password,
					use_tls=use_tls, use_ssl=use_ssl)
			else:
				conn = get_connection('django.core.mail.backends.console.EmailBackend')
			sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@sweethouse.local')
			lines = []
			for item in items:
				lines.append(f"- {item['product'].name} x{item['qty']}")
			body = "Gracias por tu compra.\n\nDetalle del pedido:\n" + "\n".join(lines) + f"\n\nTotal: ${total:,.2f}\nID(s) de solicitud: {', '.join(str(x) for x in created_ids)}"
			subject = "Confirmación de tu pedido"
			if request.user.email:
				EmailMessage(subject, body, sender, [request.user.email], connection=conn).send(fail_silently=True)
		except Exception:
			pass
		return render(request, 'tienda/checkout_exito.html', {'total': total})
	# Tomar Nequi del entorno si está disponible para reflejar cambios sin reiniciar
	nequi_number = os.environ.get('NEQUI_NUMBER', getattr(settings, 'NEQUI_NUMBER', '3000000000'))
	paypal_client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
	paypal_me_url = getattr(settings, 'PAYPAL_ME_URL', '') or os.environ.get('PAYPAL_ME_URL', '')
	paypal_email = getattr(settings, 'PAYPAL_EMAIL', '') or os.environ.get('PAYPAL_EMAIL', '')
	paypal_currency = getattr(settings, 'PAYPAL_CURRENCY', 'USD')
	if not (paypal_me_url or paypal_client_id):
		# Intentar cargar .env por si el servidor no lo hizo todavía
		load_dotenv()
		paypal_me_url = paypal_me_url or os.environ.get('PAYPAL_ME_URL', '')
		paypal_email = paypal_email or os.environ.get('PAYPAL_EMAIL', '')
	# Convertir COP -> USD si se usa USD en PayPal
	paypal_amount = total
	try:
		if paypal_currency.upper() == 'USD':
			rate = Decimal(str(getattr(settings, 'PAYPAL_COP_PER_USD', 4000.0)))
			if rate and rate > 0:
				paypal_amount = (Decimal(total) / rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
	except Exception:
		paypal_amount = Decimal(total)
	# Cadena con punto decimal para paypal.me
	try:
		paypal_amount_str = format(Decimal(paypal_amount), '0.2f')
	except Exception:
		paypal_amount_str = str(paypal_amount)
	# Determinar si la URL es de PayPal.Me para adjuntar monto
	try:
		_lower = (paypal_me_url or '').lower()
		paypal_is_me_url = ('paypal.me' in _lower) or ('paypalme' in _lower)
	except Exception:
		paypal_is_me_url = False
	return render(request, 'tienda/checkout.html', {
		'items': items,
		'total': total,
		'nequi_number': nequi_number,
		'paypal_client_id': paypal_client_id,
		'paypal_me_url': paypal_me_url,
		'paypal_email': paypal_email,
		'paypal_currency': paypal_currency,
		'paypal_amount': paypal_amount,
		'paypal_amount_str': paypal_amount_str,
		'paypal_is_me_url': paypal_is_me_url,
	})


@login_required
def pedidos_usuario(request):
	"""Listar los pedidos realizados por el usuario logueado."""
	if request.user.is_staff or request.user.is_superuser:
		messages.info(request, 'Los administradores no tienen pedidos.')
		return redirect('dashboard')
	from web.models import SolicitudPedido
	# Filtramos por el email del usuario logueado
	pedidos = SolicitudPedido.objects.filter(email=request.user.email).order_by('-created_at')
	
	context = {
		'pedidos': pedidos,
	}
	return render(request, 'tienda/pedidos_usuario.html', context)


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
			try:
				if s.email:
					subject = f"Actualización de solicitud #{s.pk} - {s.get_status_display()}"
					body = (
						f"Hola {s.name},\n\n"
						f"Tu solicitud #{s.pk} cambió al estado: {s.get_status_display()}.\n"
						f"Producto: {s.product_name}  x{s.quantity}\n"
						f"Gracias por tu confianza.\n"
						f"Sweet House"
					)
					sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@sweethouse.local')
					send_mail(subject, body, sender, [s.email], fail_silently=True)
			except Exception:
				pass
			messages.success(request, f"Estado avanzado a: {dict((k, v) for k, v in s._meta.get_field('status').choices)[s.status]}")
		else:
			messages.info(request, "La solicitud ya está en estado final: entregado.")
	except Exception:
		messages.error(request, "No se pudo avanzar el estado.")
	return redirect('solicitud_detail', pk=pk)

@staff_member_required
@require_post_method
def solicitud_enviar_email(request, pk: int):
	from web.models import SolicitudPedido
	s = get_object_or_404(SolicitudPedido, pk=pk)
	subject = (request.POST.get('subject') or '').strip() or f"Actualización de solicitud #{s.pk}"
	message = (request.POST.get('message') or '').strip()
	to_override = (request.POST.get('to_email') or '').strip()
	dest_email = s.email
	if to_override:
		try:
			validate_email(to_override)
			dest_email = to_override
		except ValidationError:
			messages.error(request, "El email del destinatario no es válido.")
			return redirect('solicitud_detail', pk=pk)
	if not s.email and not to_override:
		messages.error(request, "La solicitud no tiene email.")
		return redirect('solicitud_detail', pk=pk)
	if not message:
		messages.error(request, "Debes escribir un mensaje.")
		return redirect('solicitud_detail', pk=pk)
	sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@sweethouse.local')
	reply_to_email = (request.user.email or sender)
	import os
	host = os.environ.get('EMAIL_HOST') or getattr(settings, 'EMAIL_HOST', '')
	user = os.environ.get('EMAIL_HOST_USER') or getattr(settings, 'EMAIL_HOST_USER', '')
	password = os.environ.get('EMAIL_HOST_PASSWORD') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
	try:
		port = int(os.environ.get('EMAIL_PORT') or getattr(settings, 'EMAIL_PORT', 587))
	except Exception:
		port = 587
	use_tls = (os.environ.get('EMAIL_USE_TLS') or str(getattr(settings, 'EMAIL_USE_TLS', True))).lower() in ('true', '1', 'yes')
	use_ssl = (os.environ.get('EMAIL_USE_SSL') or str(getattr(settings, 'EMAIL_USE_SSL', False))).lower() in ('true', '1', 'yes')
	smtp_ready = bool(host and user and password)
	if smtp_ready:
		connection = get_connection(
			'django.core.mail.backends.smtp.EmailBackend',
			host=host,
			port=port,
			username=user,
			password=password,
			use_tls=use_tls,
			use_ssl=use_ssl,
		)
	else:
		connection = get_connection('django.core.mail.backends.console.EmailBackend')
	try:
		msg = EmailMessage(subject, message, sender, [dest_email], reply_to=[reply_to_email], connection=connection)
		msg.send(fail_silently=False)
		if smtp_ready:
			messages.success(request, f"Mensaje enviado a {dest_email}. Respuestas llegarán a {reply_to_email}.")
		else:
			_preview = (message or '')[:240]
			messages.warning(request, f"Correo en modo consola. Para {dest_email}. Vista previa: {_preview}")
	except Exception as e:
		messages.error(request, f"No se pudo enviar el email: {e}")
	return redirect('solicitud_detail', pk=pk)


@staff_member_required
def clientes_list(request):
    """Listar clientes priorizando usuarios registrados; combinar con emails de solicitudes sin registro."""
    from web.models import SolicitudPedido
    from django.db.models import Count, Max
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Agregados por email desde SolicitudPedido
    pedidos_aggr = {
        row['email'].lower(): row
        for row in SolicitudPedido.objects.values('email')
        .annotate(
            total_orders=Count('id'),
            last_order=Max('created_at'),
            name=Max('name'),
            phone=Max('phone')
        )
        if row['email']
    }

    clientes = []

    # Usuarios registrados (activos y no staff)
    for u in User.objects.filter(is_active=True, is_staff=False).values('first_name', 'last_name', 'username', 'email', 'date_joined'):
        email = (u['email'] or '').lower()
        ag = pedidos_aggr.get(email)
        nombre = u['first_name'] or u['username']
        clientes.append({
            'name': nombre,
            'email': u['email'] or '',
            'phone': (ag['phone'] if ag else '') or '',
            'total_orders': ag['total_orders'] if ag else 0,
            'last_order': ag['last_order'] if ag else u['date_joined'],
        })

    # Correos con pedidos pero sin usuario registrado
    for email, ag in pedidos_aggr.items():
        if not User.objects.filter(email__iexact=email).exists():
            clientes.append({
                'name': ag.get('name') or email,
                'email': ag.get('email') or email,
                'phone': ag.get('phone') or '',
                'total_orders': ag.get('total_orders') or 0,
                'last_order': ag.get('last_order'),
            })

    # Ordenar por última actividad (pedido o registro)
    clientes.sort(key=lambda x: (x['last_order'] is not None, x['last_order']), reverse=True)

    return render(request, 'tienda/clientes_list.html', {'clientes': clientes})
