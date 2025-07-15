# app/utils/mail.py
import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'wrcodesoftware@gmail.com'
    msg['To'] = to

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('wrcodesoftware@gmail.com', 'bwla tabe xdwl sjhz')
    server.send_message(msg)
    server.quit()
