from fastapi_mail import FastMail, MessageSchema
from mail.config import mail_config

async def send_reset_email(email: str, reset_link: str):

    message = MessageSchema(
        subject= "Recuperar contraseña",
        recipients= [email],
        body= f"""
            Hola,

            Recibimos una solicitud para cambiar tu contraseña.

            Haz clic aquí:

            {reset_link}

            Este enlace expirará en 30 minutos.

            Si no solicitaste este cambio, ignora este correo.
            """,

        subtype= "plain"
    )

    fm = FastMail(mail_config)

    await fm.send_message(message)