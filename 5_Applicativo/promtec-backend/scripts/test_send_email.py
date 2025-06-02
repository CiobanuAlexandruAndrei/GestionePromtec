import smtplib
from email.message import EmailMessage
import getpass

# Email details
smtp_server = "mail.infomaniak.com"
smtp_port = 465  
sender_email = "no-reply@samtrevano.ch"
receiver_email = "alexandru.ciobanu@samtrevano.ch"
subject = "Test"
body = "Test"


msg = EmailMessage()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.set_content(body)

password = "*S.z[cMyGCUGJM4&ZM"

try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, password)
        server.send_message(msg)
    print("Email sent successfully.")
except Exception as e:
    print(f"Failed to send email: {e}")
