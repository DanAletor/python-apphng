from flask import Flask, request, jsonify
from celery import Celery
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Setup logging
logging.basicConfig(filename='/var/log/messaging_system.log', level=logging.INFO)

@celery.task
def send_email_task(recipient_email):
    sender_email = "your-email@example.com"
    sender_password = "your-email-password"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Test Email'

    body = 'This is a test email sent from the Flask application using Celery.'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        logging.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {str(e)}")

@app.route('/')
def index():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')
    
    if sendmail:
        send_email_task.delay(sendmail)
        response = {'status': 'Email queued'}
    elif talktome:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"Message received at {current_time}")
        response = {'status': 'Message logged'}
    else:
        response = {'status': 'No action taken'}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

