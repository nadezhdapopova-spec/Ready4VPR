from lms.models import Course, CourseSubscription
import json

from django_celery_beat.models import PeriodicTask, IntervalSchedule


def get_subscribers_emails(course_id):
    """Возвращает список адресов электронной почты подписчиков на курс"""

    return list(
        CourseSubscription.objects.filter(course_id=course_id)
        .select_related("user")
        .values_list("user__email", flat=True)
    )


def get_course_update_mail_info(course_id):
    """Формирует заголовок и тело сообщения"""

    course = Course.objects.only("title").get(id=course_id)
    subject = "Обновление курса"
    message = (
        f"Материалы курса '{course.title}' были обновлены.\n"
        f"Возвращайтесь на наш сайт, чтобы первым увидеть обновления!"
    )
    return subject, message


schedule, created = IntervalSchedule.objects.get_or_create(
     every=24,
     period=IntervalSchedule.HOURS,
 )

PeriodicTask.objects.get_or_create(
     interval=schedule,
     name="Block nonactive users",
     task="lms.tasks.block_nonactive_user",
     args=json.dumps([]),
 )
