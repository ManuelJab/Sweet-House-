from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
from .models import SolicitudPedido
from .models import AdminRequest, CustomerFeedback
from django import forms


class AdminRequestForm(forms.ModelForm):
    class Meta:
        model = AdminRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows':4, 'placeholder':'¿Por qué necesitas acceso de administrador?'})
        }


@login_required
def request_admin(request):
    # Allow logged-in users to request admin privileges
    existing = AdminRequest.objects.filter(user=request.user).order_by('-created_at').first()
    if request.method == 'POST':
        form = AdminRequestForm(request.POST)
        if form.is_valid():
            ar = form.save(commit=False)
            ar.user = request.user
            ar.status = 'pending'
            ar.save()
            messages.success(request, 'Solicitud enviada. Un administrador la revisará.')
            return redirect('dashboard')
    else:
        form = AdminRequestForm()
    return render(request, 'web/request_admin.html', {'form': form, 'existing': existing})


def home(request):
    from tienda.models import Producto
    from .models import SolicitudPedido
    from django.db.models import Count
    mas_vendidos = []
    recomendados = []
    try:
        mas_vendidos = list(
            Producto.objects.filter(is_active=True, solicitudpedido__isnull=False)
            .annotate(ventas=Count('solicitudpedido'))
            .order_by('-ventas', 'name')[:8]
        )
        if not mas_vendidos:
            mas_vendidos = list(Producto.objects.filter(is_active=True, is_special=True).order_by('name')[:8])
    except Exception:
        mas_vendidos = list(Producto.objects.filter(is_active=True, is_special=True).order_by('name')[:8])
    try:
        recomendados = list(Producto.objects.filter(is_active=True).order_by('?')[:8])
    except Exception:
        recomendados = list(Producto.objects.filter(is_active=True).order_by('name')[:8])
    return render(request, 'index.html', {'mas_vendidos': mas_vendidos, 'recomendados': recomendados})


def catalogo(request):
    return render(request, 'catalogo.html')


def contacto(request):
    return render(request, 'contacto.html')

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = CustomerFeedback
        fields = ['name', 'email', 'comment', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tu nombre (opcional)', 'class': 'input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Tu correo (opcional)', 'class': 'input'}),
            'comment': forms.Textarea(attrs={'rows':4, 'placeholder':'Cuéntanos qué debemos mejorar...', 'class': 'textarea'}),
            'rating': forms.RadioSelect(choices=[(i, f'{i}★') for i in range(1,6)]),
        }

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save()
            try:
                send_mail(
                    subject=f'Nuevo comentario del cliente ({fb.rating}★)',
                    message=f'Nombre: {fb.name}\nEmail: {fb.email}\nRating: {fb.rating}\n\nComentario:\n{fb.comment}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                logger.exception('No se pudo enviar el correo de feedback')
            messages.success(request, 'Gracias por tu comentario. ¡Nos ayuda a mejorar!')
            return redirect('feedback')
    else:
        form = FeedbackForm()
    recientes = CustomerFeedback.objects.all()[:10]
    return render(request, 'web/feedback.html', {'form': form, 'recientes': recientes})


def solicitud_pedido(request):
    from .forms import SolicitudPedidoForm
    from tienda.models import Producto

    if request.method == 'POST':
        form = SolicitudPedidoForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # resolve product name
            producto = None
            producto_name = ''
            try:
                producto = Producto.objects.get(pk=int(data['product']))
                producto_name = producto.name
            except Exception:
                producto_name = data.get('product') or ''

            # persist the solicitud in DB
            try:
                SolicitudPedido.objects.create(
                    name=data.get('name'),
                    email=data.get('email'),
                    phone=data.get('phone') or '',
                    address=data.get('address') or '',
                    product=producto,
                    product_name=producto_name,
                    quantity=int(data.get('quantity') or 1),
                    notes=data.get('notes') or '',
                    size=data.get('size') or '',
                    event_message=data.get('event_message') or '',
                    event_date=data.get('event_date') or None,
                    occasion=data.get('occasion') or '',
                    status='recibido',
                )
            except Exception:
                logger.exception('No se pudo guardar la SolicitudPedido en la base de datos')

            subject = f"Solicitud de pedido: {data['name']} - {producto_name}"
            body = (
                f"Nombre: {data['name']}\n"
                f"Email: {data['email']}\n"
                f"Teléfono: {data.get('phone','')}\n"
                f"Dirección: {data.get('address','')}\n"
                f"Producto: {producto_name}\n"
                f"Cantidad: {data.get('quantity')}\n\n"
                f"Tamaño: {data.get('size','')}\n"
                f"Ocasión: {data.get('occasion','')}\n"
                f"Fecha del evento: {data.get('event_date','')}\n"
                f"Mensaje personalizado: {data.get('event_message','')}\n\n"
                f"Detalles adicionales:\n{data.get('notes','')}\n"
            )
            sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@stimandessert.local')
            recipient = sender
            try:
                send_mail(subject, body, sender, [recipient], fail_silently=False)
                messages.success(request, 'Solicitud enviada. Gracias, te contactaremos pronto.')
            except Exception as e:
                logger.exception('Error enviando email de solicitud_pedido')
                messages.error(request, f'Ocurrió un error al enviar la solicitud: {e}')

            return redirect('solicitud_pedido')
    else:
        form = SolicitudPedidoForm()

    # Get solicitudes saved for this user/email (last 10 submitted)
    # If user is authenticated, show their solicitudes; otherwise show from last entered email in form
    solicitudes_guardadas = []
    email_filter = None
    
    if request.user.is_authenticated:
        email_filter = request.user.email
    elif request.POST.get('email'):
        email_filter = request.POST.get('email')
    elif request.session.get('last_solicitud_email'):
        email_filter = request.session.get('last_solicitud_email')
    
    if email_filter:
        solicitudes_guardadas = SolicitudPedido.objects.filter(
            email=email_filter
        ).order_by('-created_at')[:10]
        # Store the email in session for future visits
        request.session['last_solicitud_email'] = email_filter

    return render(request, 'solicitud_pedido.html', {
        'form': form,
        'solicitudes_guardadas': solicitudes_guardadas,
        'email_filter': email_filter
    })


@login_required
def dashboard(request):
    user = request.user
    context = {
        'is_admin': user.is_superuser or user.is_staff,
        'user': user,
    }
    return render(request, 'dashboard.html', context)
