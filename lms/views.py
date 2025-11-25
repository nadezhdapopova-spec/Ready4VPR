from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Вьюсет курса"""
    serializer_class = CourseSerializer
    queryset = Course.objects.all().prefetch_related("lessons")
    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = [
        "title",
    ]


class BaseLessonAPIView(generics.GenericAPIView):
    """Базовый вьюсет урока"""
    queryset = Lesson.objects.all().select_related("category")
    serializer_class = LessonSerializer


class LessonList(BaseLessonAPIView, generics.ListAPIView):
    """Вьюсет списка уроков"""
    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = ["category", "title"]


class LessonRetrieve(BaseLessonAPIView, generics.RetrieveAPIView):
    """Вьюсет урока"""
    pass


class LessonCreate(BaseLessonAPIView, generics.CreateAPIView):
    """Вьюсет создания урока"""
    pass


class LessonUpdate(BaseLessonAPIView, generics.UpdateAPIView):
    """Вьюсет редактирования урока"""
    pass


class LessonDelete(BaseLessonAPIView, generics.DestroyAPIView):
    """Вьюсет удаления урока"""
    pass
