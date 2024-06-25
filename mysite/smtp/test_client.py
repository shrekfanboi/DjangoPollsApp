import smtplib
from email.mime.text import MIMEText

# Define the sender and recipient email addresses
sender = 'sender@example.com'
recipient = 'recipient@example.com'

# Create the email content
subject = 'Test Email'
body = 'This is a test email sent to the local SMTP server.'

# Create a MIMEText object to represent the email
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = recipient

# Connect to the local SMTP server and send the email
try:
    with smtplib.SMTP('localhost', 1025) as server:
        server.sendmail(sender, [recipient], msg.as_string())
    print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {e}')
