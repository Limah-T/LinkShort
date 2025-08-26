import smtplib, ssl, os, jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.template.loader import render_to_string
from datetime import datetime, timedelta

def expired_at():
    exp = datetime.now() + timedelta(minutes=int(os.environ.get("TOKEN_EXPIRY_MINUTES")))
    return exp.timestamp()

def encode_jwt(email):
    with open("private_key.pem", "rb") as key_file:
        private_key = key_file.read()

    payload = {
        "aud": email,
        "iat": datetime.now(),
        "exp": expired_at()
    }

    token = jwt.encode(payload=payload, key=private_key, algorithm=os.environ.get("ALGORITHM"))
    return token

def decode_jwt(token):
    with open("public_key.crt", "rb") as key_file:
        public_key = key_file.read()
    try:
        payload = jwt.decode(token, public_key, algorithms=[os.environ.get("ALGORITHM")])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except jwt.InvalidTokenError:
        print("Invalid token")

smtp_server = os.environ.get("EMAIL_HOST") 
port = os.environ.get("EMAIL_PORT")  
sender_email = os.environ.get("EMAIL_HOST_USER") 
host = os.environ.get("ADMIN_EMAIL")
password = os.environ.get("EMAIL_HOST_PASSWORD") 

def send_verification_email(to_email, subject, template_name, text_template_name):
    token = encode_jwt(to_email)
    verification_url = f"http://127.0.0.1:8000/api/v1/verify?token={token}"
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    html = render_to_string(template_name, {"VERIFICATION_LINK": verification_url})
    text = render_to_string(text_template_name, {"VERIFICATION_LINK": verification_url})
    msg.attach(MIMEText(html, "html"))  # can use "plain" too
    msg.attach(MIMEText(text, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port, timeout=60) as server:
        server.ehlo()  # optional, but recommended
        server.starttls(context=context)  # TLS handshake
        server.ehlo()
        server.login(host, password)
        server.sendmail(sender_email, to_email, msg.as_string())
        print(verification_url)
