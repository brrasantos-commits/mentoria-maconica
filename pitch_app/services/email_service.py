import smtplib
import logging
from email.mime.text import MIMEText
import os

logger = logging.getLogger(__name__)

def send_reset_email(to_email: str, reset_link: str):
    """Send password reset email"""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    # Verificar se configurações SMTP estão presentes
    if not all([smtp_host, smtp_user, smtp_password]):
        logger.warning("SMTP not configured. Email not sent.")
        logger.info(f"Reset link for {to_email}: {reset_link}")
        return

    subject = "Redefinição de senha - Sales Pitch AI"
    body = f"""
Olá,

Você solicitou a redefinição de senha no Sales Pitch AI.

Clique no link abaixo para redefinir sua senha:

{reset_link}

Este link expira em 1 hora.

Se você não solicitou esta redefinição, ignore este email.

---
Sales Pitch AI
"""

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = to_email

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Reset email sent successfully to {to_email}")
    
    except Exception as e:
        logger.error(f"Failed to send reset email to {to_email}: {e}")
        raise