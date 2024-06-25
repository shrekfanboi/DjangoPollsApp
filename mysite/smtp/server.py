import aiosmtpd
import asyncio
from email.message import EmailMessage
from aiosmtpd.controller import Controller
from datetime import datetime
import os

class MyController:
    async def handle_DATA(self, server, session, envelope):
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        data = envelope.content.decode("utf8", errors="replace")
        print(f"Received message from {mail_from} to {rcpt_tos}")

        message = EmailMessage()
        message.set_content(data)
        message['From'] = mail_from
        message['To'] = ', '.join(rcpt_tos)
        message['Subject'] = 'Test Email'
        message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

        os.makedirs('emails', exist_ok=True)

        # Save the email content to a .eml file
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.eml'
        filepath = os.path.join('emails', filename)
        with open(filepath, 'w') as f:
            f.write(message.as_string())

        return '250 Message accepted for delivery'

controller = Controller(handler=MyController(), hostname='localhost', port=1025)
controller.start()

async def main():
    try:
        print('Listening on port 1025. Ctrl-C to quit.')
        await asyncio.Event().wait() 
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()

asyncio.run(main())
