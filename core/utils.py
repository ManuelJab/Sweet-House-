import os
import json
import urllib.request
import urllib.error
from email.utils import parseaddr
from django.conf import settings

def enviar_correo(destinatario, asunto, contenido):
    url = "https://api.brevo.com/v3/smtp/email"
    
    api_key = os.getenv("BREVO_API_KEY") or getattr(settings, "BREVO_API_KEY", "")
    if not api_key or api_key == "TU_API_KEY":
        raise RuntimeError("BREVO_API_KEY no está configurada")

    sender_name = os.getenv("BREVO_SENDER_NAME", "Sweet House")
    sender_email = os.getenv("BREVO_SENDER_EMAIL", "").strip()
    if not sender_email:
        sender_email = parseaddr(getattr(settings, "DEFAULT_FROM_EMAIL", ""))[1].strip()
    if not sender_email:
        raise RuntimeError("BREVO_SENDER_EMAIL / DEFAULT_FROM_EMAIL no está configurado")

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email
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

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = (e.read().decode("utf-8") if hasattr(e, "read") else "") or "{}"
        try:
            payload_err = json.loads(raw)
        except Exception:
            payload_err = {"error": raw}
        raise RuntimeError(f"Brevo HTTP {getattr(e, 'code', 'error')}: {payload_err}") from e
