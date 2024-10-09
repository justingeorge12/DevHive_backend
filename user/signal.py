
from django.db.models.signals import post_save
from . models import Users
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

import pyotp 


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.now()
    return otp[:5]

def send_otp_email(email, otp):
    subject = 'YOUR OTP CODE'
    message = f'your otp code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


@receiver(post_save, sender = Users)
def generate_otp_and_send(sender, instance, created, *args, **kwargs):
    if created:
        otp = generate_otp()
        instance.otp = otp
        instance.save()

        send_otp_email(instance.email, otp)
    