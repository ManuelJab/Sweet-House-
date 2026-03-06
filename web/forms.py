from django import forms
from tienda.models import Producto


class SolicitudPedidoForm(forms.Form):
    name = forms.CharField(label='Nombre completo', max_length=120)
    email = forms.EmailField(label='Correo electrónico')
    phone = forms.CharField(label='Número de teléfono', max_length=30, required=False)
    address = forms.CharField(label='Dirección de envío', max_length=250, required=False)
    product = forms.ChoiceField(label='Producto', choices=[], required=True)
    quantity = forms.IntegerField(label='Cantidad', min_value=1, initial=1)
    notes = forms.CharField(label='Detalles / Observaciones', required=False, widget=forms.Textarea(attrs={'rows':4}))
    # Personalización
    size = forms.ChoiceField(label='Tamaño', choices=[('pequeño','Pequeño'),('mediano','Mediano'),('grande','Grande')], required=False)
    event_message = forms.CharField(label='Mensaje personalizado', max_length=200, required=False)
    event_date = forms.DateField(label='Fecha del evento', required=False, widget=forms.DateInput(attrs={'type':'date'}))
    occasion = forms.ChoiceField(label='Ocasión', choices=[('cumpleaños','Cumpleaños'),('aniversario','Aniversario'),('grado','Grado'),('otro','Otro')], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        productos = Producto.objects.filter(is_active=True).order_by('name')
        choices = [('', 'Por favor seleccione')] + [(str(p.id), p.name) for p in productos]
        self.fields['product'].choices = choices
