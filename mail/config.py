import os
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")