
from django.db.models.signals import post_save
from . models import Users
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import datetime

from django.template.loader import render_to_string
from django.utils.html import strip_tags

import pyotp 


def generate_otp():
    print('calll cammmeeeeeeeeeeeeeeee here from generate otppppppppp')
    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.now()
    print('otp gggggoooooooooooooooooooooooooooone')
    return otp[:5]

def send_otp_email(email,name, otp):
    subject = 'YOUR OTP CODE'
    context =  {
        'username' : name,
        'otp' : otp,
        'year' : datetime.datetime.now().year,
    }
    html_msg = render_to_string('otp.html', context)
    plain_msg = strip_tags(html_msg)

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, plain_msg, email_from, recipient_list, html_message=html_msg)


@receiver(post_save, sender = Users)
def generate_otp_and_send(sender, instance, created, *args, **kwargs):
    if created:
        otp = generate_otp()
        instance.otp = otp
        instance.save()

        send_otp_email(instance.email, instance.username, otp)
    