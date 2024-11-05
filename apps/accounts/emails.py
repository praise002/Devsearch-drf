import random
import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Otp


def generate_otp(user):
    otp = random.randint(100000, 999999)
    # Save the OTP to the Otp model
    Otp.objects.create(user=user, otp=otp)
    return otp


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class SendEmail:

    @staticmethod
    def send_otp(request, user):
        domain = f"{request.scheme}://{request.get_host()}"  # http www.example.com
        otp = generate_otp(user)
        subject = "Verify your email"
        email = user.email
        context = {
            "domain": domain,
            "name": user.full_name,
            "email": email,
            "otp": otp,
        }
        message = render_to_string("otp_email_message.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def welcome(request, user):
        domain = f"{request.scheme}://{request.get_host()}"
        subject = "Account Verified"
        context = {
            "domain": domain,
            "name": user.full_name,
        }
        message = render_to_string("welcome_message.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def send_password_reset_otp(request, user):
        domain = f"{request.scheme}://{request.get_host()}"  # http www.example.com
        otp = generate_otp(user)
        subject = "Your Password Reset OTP"
        email = user.email
        context = {
            "domain": domain,
            "name": user.full_name,
            "email": email,
            "otp": otp,
        }
        message = render_to_string("password_reset_otp.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def password_reset_success(request, user):
        domain = f"{request.scheme}://{request.get_host()}"
        subject = "Password Reset Successful"
        context = {
            "domain": domain,
            "name": user.full_name,
        }
        message = render_to_string("password_reset_success.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
