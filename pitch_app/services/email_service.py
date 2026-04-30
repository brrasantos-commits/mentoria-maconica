import smtplib
from email.mime.text import MIMEText
import os

def send_reset_email(to_email: str, reset_link: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    subject = "Redefinição de senha"
    body = f"""
Olá,

Clique no link abaixo para redefinir sua senha:

{reset_link}

Se você não solicitou, ignore este email.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)