from django.db import models


class Course(models.Model):
    """Модель курса"""

    title = models.CharField(max_length=100, unique=True, verbose_name="Наименование курса")
    preview = models.ImageField(
        upload_to="lms/courses/previews/",
        blank=True,
        null=True,
        verbose_name="Изображение",
        default="default/default.png",
        help_text="Необязательное поле",
    )
    description = models.TextField(null=True, blank=True, verbose_name="Описание курса")
    owner = models.ForeignKey(to="users.CustomUser", on_delete=models.SET_NULL, related_name="users", null=True)

    def __str__(self):
        """Строковое отображение курса"""
        return self.title

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"
        ordering = [
            "title",
        ]


def get_default_course():
    """Устанавливает курс по умолчанию 'Вне курса'"""

    course, created = Course.objects.get_or_create(
        title="Вне курса", defaults={"description": "Дополнительно, вне курса"}
    )
    return course.id


class Lesson(models.Model):
    """Модель урока"""

    title = models.CharField(max_length=100, unique=True, verbose_name="Наименование урока")
    description = models.TextField(null=True, blank=True, verbose_name="Описание урока")
    preview = models.ImageField(
        upload_to="lms/lessons/previews/",
        blank=True,
        null=True,
        verbose_name="Изображение",
        default="default/default.png",
        help_text="Необязательное поле",
    )
    video_link = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="Ссылка на видео", help_text="Необязательное поле"
    )
    category = models.ForeignKey(
        to=Course, on_delete=models.CASCADE, related_name="lessons", default=get_default_course
    )
    owner = models.ForeignKey(to="users.CustomUser", on_delete=models.SET_NULL, related_name="user", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    def __str__(self):
        """Строковое отображение урока"""
        return self.title

    class Meta:
        verbose_name = "урок"
        verbose_name_plural = "уроки"
        ordering = [
            "title",
        ]


class CourseSubscription(models.Model):
    """Модель подписки пользователя на обновления курса"""

    user = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        related_name="subscribers",
    )
    course = models.ForeignKey(
        to=Course,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "подписка на курс"
        verbose_name_plural = "подписки на курсы"

    def __str__(self):
        return f"{self.user} - {self.course}"
