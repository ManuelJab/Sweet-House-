import threading
import logging
from django.core.mail.backends.smtp import EmailBackend

# Logger para depuración en producción (Render/Heroku)
logger = logging.getLogger(__name__)

class AsyncEmailBackend(EmailBackend):
    """
    Motor de correo asíncrono robusto para evitar bloqueos en la interfaz.
    """
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        # Enviamos en un hilo NO-daemon para asegurar que se complete el envío
        # incluso si la respuesta HTTP ya se envió.
        thread = threading.Thread(target=self._send_messages_sync, args=(email_messages,))
        thread.start()
        
        return len(email_messages)

    def _send_messages_sync(self, email_messages):
        try:
            # Importante: Cada hilo debe manejar su propia conexión SMTP
            # super().send_messages ya se encarga de abrir y cerrar la conexión.
            sent_count = super().send_messages(email_messages)
            if sent_count:
                print(f"✅ [AsyncEmail] {sent_count} correos enviados.")
        except Exception as e:
            print(f"❌ [AsyncEmail Error] Fallo: {str(e)}")
            logger.error(f"Error enviando correo asíncrono: {e}", exc_info=True)
