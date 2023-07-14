import smtplib
import ssl, os
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()

# Define email sender and receiver
email_sender = os.getenv('SMTP_GMAIL_EMAIL_SENDER')
email_password = os.getenv('SMTP_GMAIL_PASSWORD')

def send_email(receiver:str, subject:str, message:str):

    # Set the subject and body of the email
    subject = subject
    body = message
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, receiver, em.as_string())

if __name__ == '__main__':
    email_reciever=os.getenv('SMTP_GMAIL_EMAIL_RECIEVER')
    send_email(email_reciever, 'TEST SUBJECT', 'TEST BODY')