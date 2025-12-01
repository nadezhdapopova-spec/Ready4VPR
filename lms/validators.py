from urllib.parse import urlparse

from rest_framework.serializers import ValidationError


class VideoLinkValidator:
    """
    Валидатор поля 'Ссылка на видео' модели Урока.
    Проверяет отсутствие в материалах ссылок на сторонние ресурсы, кроме youtube.com
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            return value

        allowed_domains = [
            "www.youtube.com",
            "youtube.com",
            "youtu.be",
            "www.youtu.be",
        ]
        parsed = urlparse(value)
        domain = parsed.netloc

        if domain not in allowed_domains:
            raise ValidationError("Разрешены только ссылки на YouTube")
        return value
