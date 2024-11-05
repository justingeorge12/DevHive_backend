from django.db.models.signals import post_save
from . models import Answers, Question
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import datetime

from django.template.loader import render_to_string
from django.utils.html import strip_tags


def create_email_content(email, username, question):
    subject = 'YOUR QUESTION GET ANSWERED'
    context = {
        'username' : username,
        'question' : question,
        'year' : datetime.datetime.now().year,
    }
    html_msg = render_to_string('answeremail.html', context)
    plain_msg = strip_tags(html_msg)

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, plain_msg, email_from, recipient_list, html_message=html_msg)



@receiver(post_save, sender = Answers)
def create_instance(instance, created, *args, **kwargs):
    if created:
        try:
            question_user = instance.question.user.id 
            answer_user = instance.user.id

            if question_user != answer_user:
                create_email_content(instance.question.user.email, instance.question.user.username, instance.question.title )
                print('gone from here')

        except Exception as e:
            print('instance isssue', e)







