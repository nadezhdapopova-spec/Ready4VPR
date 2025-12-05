from datetime import datetime

from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from lms.services import get_course_update_mail_info, get_subscribers_emails
from users.models import CustomUser





@shared_task
def send_course_update_email(course_id):
    emails = get_subscribers_emails(course_id)
    subject, message = get_course_update_mail_info(course_id)
    send_mail(subject=subject, message=message, recipient_list=emails, from_email=EMAIL_HOST_USER)
