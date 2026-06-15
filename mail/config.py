import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv()

mail_config = ConnectionConfig(

    MAIL_USERNAME= os.getenv("SMTP_USER"),
    MAIL_PASSWORD= os.getenv("SMTP_PASSWORD"),
    MAIL_FROM= os.getenv("SMTP_FROM"),
    MAIL_SERVER= os.getenv("SMTP_HOST"),
    MAIL_PORT= int(os.getenv("SMTP_PORT")),

    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True
)