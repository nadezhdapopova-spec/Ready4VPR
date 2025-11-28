from rest_framework import serializers

from lms.models import Course, Lesson, CourseSubscription
from lms.validators import VideoLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока"""

    category = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    video_link = serializers.URLField(
        required=False,
        allow_blank=True,
        validators=[VideoLinkValidator(field="video_link")]
    )

    class Meta:
        model = Lesson
        fields = ("id", "title", "preview", "description", "video_link", "category", "owner")



class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса"""

    lessons_amount = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()

    @staticmethod
    def get_lessons_amount(instance):
        """Возвращает количество уроков в курсе"""
        return instance.lessons.count()

    def get_is_subscribed(self, obj):
        """Возвращает булевое значение для поля подписки пользователем на курс"""
        user = self.context.get("request").user
        if user.is_authenticated:
            return CourseSubscription.objects.filter(user=user, course=obj, is_active=True).exists()
        return False

    class Meta:
        model = Course
        fields = ("id", "title", "preview", "description", "lessons_amount", "lessons", "is_subscribed")
