import smtplib

from email.mime.text import MIMEText

SMTP_HOST = 'localhost'
SMTP_PORT = 1025
FROM_EMAIL = 'institute@email.com'

def sendEmail(toEmail, subject, body, type='plain'):
    msg = MIMEText(body, type, 'utf-8')
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = toEmail

    if type == 'csv':
            msg.add_header('Content-Disposition', 'attachment; filename="data.csv"')

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        print(f"Email sent to {toEmail}")
    except Exception as e:
        print(f"Failed to sent email : {e}")

    return True
