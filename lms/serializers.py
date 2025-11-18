from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока"""
    category = serializers.StringRelatedField()

    class Meta:
        model = Lesson
        fields = ("id", "title", "preview", "description", "video_link", "category")


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса"""

    lessons_amount = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    @staticmethod
    def get_lessons_amount(instance):
        """Возвращает количество уроков в курсе"""
        return instance.lessons.count()

    class Meta:
        model = Course
        fields = ("id", "title", "preview", "description", "lessons_amount", "lessons")
