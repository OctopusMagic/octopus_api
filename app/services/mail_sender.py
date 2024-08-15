import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

from loguru import logger
import requests

from app.config.cfg import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

def send_mail(send_to, subject, message, send_from=SMTP_USER, files=[],
              server=SMTP_HOST, port=SMTP_PORT, username=SMTP_USER,
              password=SMTP_PASSWORD, use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(message))

        for path in files:
            # Files are URLs, so we need to download them first
            response = requests.get(path)
            part = MIMEBase('application', "octet-stream")
            part.set_payload(response.content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename="{Path(path).name}"')
            msg.attach(part)

        smtp = smtplib.SMTP_SSL(server)
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()
    except Exception as e:
        logger.error(f"Error sending email: {e}")
