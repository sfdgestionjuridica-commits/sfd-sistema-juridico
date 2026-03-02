import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_USER, EMAIL_PASSWORD


def enviar_email(destinatario, asunto, mensaje_html):

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = destinatario
        msg["Subject"] = asunto

        msg.attach(MIMEText(mensaje_html, "html"))

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_USER, EMAIL_PASSWORD)

        servidor.sendmail(EMAIL_USER, destinatario, msg.as_string())
        servidor.quit()

        print(f"📧 Email enviado correctamente a {destinatario}")

    except Exception as e:
        raise Exception(f"❌ ERROR REAL EMAIL: {e}")