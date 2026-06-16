import resend
from mail.config import RESEND_API_KEY, MAIL_FROM

resend.api_key = RESEND_API_KEY


def send_reset_email(email: str, reset_link: str):

    resend.Emails.send({

        "from": MAIL_FROM,
        "to": email,
        "subject": "Recuperar contraseña",
        "text": f"""
Hola,

Recibimos una solicitud para cambiar tu contraseña.

Haz clic en el siguiente enlace:

{reset_link}

Este enlace expirará en 30 minutos.

Si no solicitaste este cambio, puedes ignorar este correo.

Equipo de Evoruna
"""

    })