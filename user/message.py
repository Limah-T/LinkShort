from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime, timedelta, timezone
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError, SMTPException
from dotenv import load_dotenv
import jwt, socket, os, kickbox, json

load_dotenv(override=True)

def expiration_time(minutes):
    expiry_in = datetime.now(timezone.utc) + timedelta(minutes=minutes) 
    return expiry_in

def get_token(user):
    expiry = expiration_time(int(os.getenv("EXPIRATION_TIME")))
    now = datetime.now(timezone.utc)
    PAYLOAD = {
        'iat': int(now.timestamp()),
        'exp': int(expiry.timestamp()),
        'sub': user
    }
     
    with open("private.pem", 'r') as file:
        KEY = file.read()
    encode = jwt.encode(payload=PAYLOAD, key=KEY, algorithm=os.getenv("ALGO"))
    return encode
        

def send_token_for_email_verification(user):
    token = get_token(user=user)
    URL = f"{os.getenv('URL')}?token={token}"
    print(URL)
    SUBJECT = "Email Verification"

    html_content = render_to_string(
                            template_name="account/email_verification.html",
                            context={
                                "VERIFICATION_URL":URL,
                                "subject":SUBJECT
                            }
                        )
    msg = EmailMultiAlternatives(
        subject=SUBJECT,
        from_email=os.getenv("EMAIL_HOST_USER"),
        to=[user]
    )
    msg.attach_alternative(content=html_content, mimetype="text/html")

    try:
        msg.send()
        print("sent")
        return True
    except SMTPAuthenticationError:
        print("SMTP Authentication failed. Check your email credentials.")
        return None
    except SMTPConnectError:
        print("Failed to connect to the SMTP server. Is it reachable?")
        return None
    except SMTPRecipientsRefused:
        print("Recipient address was refused by the server.")
        return None
    except SMTPSenderRefused:
        print("Sender address was refused by the server.")
        return None
    except SMTPDataError:
        print("SMTP server replied with an unexpected error code (data issue).")
        return None
    except SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return None
    except socket.gaierror:
        print("Network error: Unable to resolve SMTP server.")
        return None
    except socket.timeout:
        print("Network error: SMTP server timed out.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
def decode_token(token):

    with open ('public.pem', 'r') as file:
        KEY = file.read()

    try:
        decoded_token = jwt.decode(jwt=token, key=KEY, algorithms=[os.getenv("ALGO")])
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired!")
        return None
    except jwt.InvalidTokenError:
        print("Token is invalid")
        return None
    
def send_token_for_password_reset(user):
    print("Here 1")
    token = get_token(user=user)
    URL = f"{os.getenv('PASSWORD_URL')}?token={token}"
    print("here 2")
    print(URL)
    SUBJECT = "Reset Password"

    html_content = render_to_string(
                            template_name="account/password_reset_email.html",
                            context={
                                "VERIFICATION_URL":URL,
                                "subject":SUBJECT
                            }
                        )
    msg = EmailMultiAlternatives(
        subject=SUBJECT,
        from_email=os.getenv("EMAIL_HOST_USER"),
        to=[user]
    )
    msg.attach_alternative(content=html_content, mimetype="text/html")

    try:
        msg.send()
        print("sent")
        return True
    except SMTPAuthenticationError:
        print("SMTP Authentication failed. Check your email credentials.")
        return None
    except SMTPConnectError:
        print("Failed to connect to the SMTP server. Is it reachable?")
        return None
    except SMTPRecipientsRefused:
        print("Recipient address was refused by the server.")
        return None
    except SMTPSenderRefused:
        print("Sender address was refused by the server.")
        return None
    except SMTPDataError:
        print("SMTP server replied with an unexpected error code (data issue).")
        return None
    except SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return None
    except socket.gaierror:
        print("Network error: Unable to resolve SMTP server.")
        return None
    except socket.timeout:
        print("Network error: SMTP server timed out.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def send_contact_message(email, name, sub, message):
    html_content = render_to_string(
                            template_name="account/contact_message.html",
                            context={
                                "name": name,
                                "email": email,
                                "subject": sub,
                                "message": message
                            }
                        )

    msg = EmailMultiAlternatives(
        subject=f"AskMe Contact: {sub}",
        from_email=os.getenv("EMAIL_HOST_USER"),  # the verified sender
        to=[email]        
        # reply_to=[email]  # user’s email in Reply-To header
)
    msg.attach_alternative(content=html_content, mimetype="text/html")

    try:
        msg.send()
        print("sent")
        return True
    except SMTPAuthenticationError:
        print("SMTP Authentication failed. Check your email credentials.")
        return None
    except SMTPConnectError:
        print("Failed to connect to the SMTP server. Is it reachable?")
        return None
    except SMTPRecipientsRefused:
        print("Recipient address was refused by the server.")
        return None
    except SMTPSenderRefused:
        print("Sender address was refused by the server.")
        return None
    except SMTPDataError as e:
        print(f"SMTPDataError: {e.smtp_code} - {e.smtp_error.decode()}")
        return None
    except SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return None
    except socket.gaierror:
        print("Network error: Unable to resolve SMTP server.")
        return None
    except socket.timeout:
        print("Network error: SMTP server timed out.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
def verify_email_from_kickbox(email):
    import kickbox
    client   = kickbox.Client(os.getenv('KICK_API'))
    kickbox  = client.kickbox()
    response = kickbox.verify(email)
    json.dumps(response.body, indent=2)
    return response.body