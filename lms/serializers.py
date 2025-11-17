from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    lessons_amount = serializers.SerializerMethodField()

    @staticmethod
    def get_lessons_amount(instance):
        return instance.lessons.count()

    class Meta:
        model = Course
        fields = ("id", "title", "preview", "description", "lessons_amount")


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "preview", "description", "video_link", "category")
