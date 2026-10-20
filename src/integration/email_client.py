import ssl
import smtplib
from email.mime.text import MIMEText
from src.domain.errors import ServiceUnavailable
from src import config



def send_mail( receiver_mail, subject, body):      

        message = MIMEText(body)
        message["From"] = config.SMTP_USER
        message["To"] = receiver_mail
        message["Subject"] = subject

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, context=context) as server:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.sendmail(config.SMTP_USER, receiver_mail, message.as_string())
        except (smtplib.SMTPException, OSError):
            raise ServiceUnavailable("Could not send the email. Please try again later.")
             
           
