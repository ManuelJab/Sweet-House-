import requests
import os
from django.conf import settings

def enviar_correo(destinatario, asunto, contenido):
    """
    Envía un correo utilizando la API de Brevo (V3).
    """
    url = "https://api.brevo.com/v3/smtp/email"
    
    # Obtenemos la API KEY desde las variables de entorno para seguridad
    api_key = os.getenv("BREVO_API_KEY", "TU_API_KEY")

    payload = {
        "sender": {
            "name": "Sweet-House",
            "email": "manuelarrietabarreto20@gmail.com"
        },
        "to": [{"email": destinatario}],
        "subject": asunto,
        "htmlContent": contenido
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error enviando correo por API: {e}")
        return None
