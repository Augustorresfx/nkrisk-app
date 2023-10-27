from django.conf import settings
import os
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from datetime import timedelta, datetime
from ..models import Cobranza
from openpyxl import load_workbook
from pathlib import Path
from datetime import date
from django.utils import timezone
from openpyxl.utils import get_column_letter
from django.db.models import Q
import environ
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

env = environ.Env()
environ.Env.read_env()

SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

def expiracion_cobranzas():
    # Obtén los objetos cuya fecha de expiración es dentro de una semana
    expiration_date = datetime.today() + timedelta(days=7)
    objects_to_remind = Cobranza.objects.filter(fecha_vencimiento=expiration_date)

    # Agrupa los objetos en un solo correo
    recipients = ['augustorresfx@gmail.com']  # Agrega las direcciones de correo destinatario

    if objects_to_remind:
        subject = 'Notificación de vencimiento de pólizas'
        from_email = SMTP_USER  # Cambia esto a tu dirección de correo

        # Genera el contenido del correo electrónico
        plaintext = get_template('email_template.txt')
        htmly = get_template('email_template.html')

        d = {
            'objects_to_remind': objects_to_remind,
        }

        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        # Crea el correo electrónico
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")

        # Envía el correo electrónico
        msg.send()