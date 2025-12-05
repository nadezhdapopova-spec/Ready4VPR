from datetime import datetime

from django.core.mail import send_mail

from celery import shared_task

from config.settings import EMAIL_HOST_USER
from lms.services import get_course_update_mail_info, get_subscribers_emails
from users.models import CustomUser


@shared_task
def block_nonactive_user():
    users = CustomUser.objects.filter(is_stuff=False).all()
    for user in users:
        time_delta = datetime.now() - user.last_login
        if time_delta.days > 30:
            user.is_active = False
            user.save()
            print("done")
        print("no nonactive_user")

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_course_update_email(self, course_id):
    """Отправляет сообщение пользователю об обновлении куса, на который он подписан"""

    emails = get_subscribers_emails(course_id)
    subject, message = get_course_update_mail_info(course_id)
    try:
        send_mail(subject=subject, message=message, recipient_list=emails, from_email=EMAIL_HOST_USER)
    except Exception as exc:
        raise self.retry(exc=exc)
