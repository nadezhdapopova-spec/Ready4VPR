from lms.models import CourseSubscription, Course


def get_subscribers_emails(course_id):
    return list(
        CourseSubscription.objects
        .filter(course_id=course_id)
        .select_related("user")
        .values_list("user__email", flat=True)
    )


def get_course_update_mail_info(course_id):
    course = Course.objects.only("title").get(id=course_id)
    subject = "Обновление курса"
    message = (f"Материалы курса '{course.title}' были обновлены.\n"
               f"Возвращайтесь на наш сайт, чтобы первым увидеть обновления!")
    return subject, message
