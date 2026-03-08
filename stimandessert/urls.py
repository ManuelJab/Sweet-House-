from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from tienda.views import admin_dashboard, CustomLoginView, home
from web.views import solicitud_pedido, request_admin, feedback
from tienda.forms import EmailAuthenticationForm
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('catalogo/', RedirectView.as_view(url='/tienda/catalogo/', permanent=False), name='catalogo'),
    path('contacto/', TemplateView.as_view(template_name='contacto.html'), name='contacto'),
    path('comentarios/', feedback, name='feedback'),
    path('solicitud/', solicitud_pedido, name='solicitud_pedido'),
    path('dashboard/', admin_dashboard, name='dashboard'),
    # Use a custom authentication form that asks for email (stored in User.username)
    path('accounts/login/', CustomLoginView.as_view(
        template_name='registration/login.html',
        authentication_form=EmailAuthenticationForm
    ), name='login'),
    path('accounts/request-admin/', request_admin, name='request_admin'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('tienda/', include('tienda.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
