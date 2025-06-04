# emailer.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import os # For getting password from environment variable

def load_config(config_path="config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def send_email(subject, html_content, recipients, config):
    smtp_config = config['smtp']
    # IMPORTANT: Get password, sender_email from environment variable (set by GitHub Secrets)
    sender_email = os.environ.get('SMTP_USERNAME')
    if not sender_email:
        print("Error: SMTP_USERNAME environment variable not set.")
        return False
    password = os.environ.get('SMTP_PASSWORD')
    if not password:
        print("Error: SMTP_PASSWORD environment variable not set.")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    # Sending to multiple recipients, join them for the 'To' header
    message["To"] = ", ".join(recipients)

    # Attach HTML part
    part_html = MIMEText(html_content, "html")
    message.attach(part_html)

    try:
        if smtp_config.get('use_ssl', False): # Port 465
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'], context=context)
        else: # Port 587 (TLS) or other
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            if smtp_config.get('use_tls', True): # Default to TLS for port 587
                context = ssl.create_default_context()
                server.starttls(context=context)

        server.login(sender_email, password)
        server.sendmail(sender_email, recipients, message.as_string())
        print(f"Email sent successfully to {', '.join(recipients)}!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    finally:
        if 'server' in locals() and server:
            server.quit()